import json
import re
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import ChoiceFormSet, QuestionSetCreateForm, TeacherQuestionForm
from .models import Answer, FreeAnnotation, Question, QuestionSet, Submission


def home(request):
    question_sets = (
        QuestionSet.objects
        .annotate(
            question_count=Count("items", distinct=True),
            submission_count=Count("submissions", distinct=True),
        )
        .order_by("-created_at")
    )
    return render(request, "assessments/teacher_home.html", {
        "question_sets": question_sets,
    })


def teacher_create_set(request):
    if request.method == "POST":
        form = QuestionSetCreateForm(request.POST)
        if form.is_valid():
            question_set = form.save()
            return redirect("teacher_set_created", public_id=question_set.public_id)
    else:
        form = QuestionSetCreateForm()
    return render(request, "assessments/teacher_create_set.html", {"form": form})


def teacher_set_created(request, public_id):
    question_set = get_object_or_404(QuestionSet, public_id=public_id)
    student_url = request.build_absolute_uri(reverse("student_take_set", args=[public_id]))
    return render(request, "assessments/teacher_set_created.html", {
        "question_set": question_set,
        "student_url": student_url,
    })



def teacher_question_bank(request):
    questions = Question.objects.filter(
        question_type__in=[Question.Type.MATHLIVE, Question.Type.MULTIPLE_CHOICE, Question.Type.MULTI_SELECT, Question.Type.YES_NO_MATRIX, Question.Type.GRID_LINE_DRAWING, Question.Type.EQUATION_BUILDER, Question.Type.NUMBER_LINE_DRAG, Question.Type.DRAG_DROP_IMAGE]
    ).prefetch_related("choices").order_by("-id")
    return render(request, "assessments/teacher_question_bank.html", {"questions": questions})

def _choice_formset(question, data=None):
    fs = ChoiceFormSet(data=data, instance=question, prefix="choices")
    if not data:
        for i, f in enumerate(fs.forms):
            if f.instance.pk:
                if question.question_type == Question.Type.YES_NO_MATRIX:
                    try:
                        matrix_expected = json.loads(question.correct_answer or "{}")
                    except json.JSONDecodeError:
                        matrix_expected = {}
                    f.fields["is_correct"].initial = bool(matrix_expected.get(f.instance.value, False))
                elif question.question_type == Question.Type.MULTI_SELECT:
                    try:
                        f.fields["is_correct"].initial = f.instance.value in json.loads(question.correct_answer or "[]")
                    except json.JSONDecodeError:
                        f.fields["is_correct"].initial = False
                else:
                    f.fields["is_correct"].initial = f.instance.value == question.correct_answer
            else:
                f.fields["order"].initial = i
                f.fields["value"].initial = f"choice_{i+1}"
    return fs

def _validate_mc(form, fs):
    nonblank, correct = 0, 0
    for cf in fs.forms:
        if cf.cleaned_data and not cf.cleaned_data.get("DELETE") and (cf.cleaned_data.get("text") or "").strip():
            nonblank += 1
            correct += bool(cf.cleaned_data.get("is_correct"))
    qtype = form.cleaned_data.get("question_type")
    if nonblank < 2:
        form.add_error(None, "Choice questions need at least two answer choices.")
        return False
    if qtype == Question.Type.MULTIPLE_CHOICE and correct != 1:
        form.add_error(None, "Select exactly one correct answer.")
        return False
    if qtype == Question.Type.MULTI_SELECT and correct < 1:
        form.add_error(None, "Select at least one correct answer.")
        return False
    # Yes/No Matrix uses checked = Yes and unchecked = No, so zero checked rows is valid.
    return True

def _save_question(form, fs):
    q = form.save(commit=False)
    q.drag_config = {}
    q.save()
    if q.question_type in [Question.Type.MULTIPLE_CHOICE, Question.Type.MULTI_SELECT, Question.Type.YES_NO_MATRIX]:
        kept, correct_values = [], []
        for i, cf in enumerate(fs.forms):
            if not cf.cleaned_data or cf.cleaned_data.get("DELETE"):
                continue
            text = (cf.cleaned_data.get("text") or "").strip()
            if not text:
                continue
            c = cf.save(commit=False)
            c.question = q
            c.order = i
            c.value = c.value or f"choice_{i+1}"
            c.save()
            kept.append(c.id)
            if cf.cleaned_data.get("is_correct"):
                correct_values.append(c.value)
        q.choices.exclude(id__in=kept).delete()
        
        if q.question_type == Question.Type.MULTI_SELECT:
            q.correct_answer = json.dumps(correct_values)
        elif q.question_type == Question.Type.YES_NO_MATRIX:
            # For matrix authoring, a checked Correct box means Yes; unchecked means No.
            q.correct_answer = json.dumps({c.value: (c.value in correct_values) for c in q.choices.filter(id__in=kept)})
        else:
            q.correct_answer = correct_values[0] if correct_values else ""
        q.save(update_fields=["correct_answer"])
    else:
        q.choices.all().delete()
    return q

def teacher_question_create(request):
    q = Question(question_type=Question.Type.MATHLIVE, is_active=True)
    form = TeacherQuestionForm(request.POST or None, instance=q)
    fs = _choice_formset(q, request.POST if request.method == "POST" else None)
    if request.method == "POST":
        fs_ok = fs.is_valid()
        if form.is_valid() and fs_ok:
            if form.cleaned_data["question_type"] not in [Question.Type.MULTIPLE_CHOICE, Question.Type.MULTI_SELECT, Question.Type.YES_NO_MATRIX] or _validate_mc(form, fs):
                _save_question(form, fs)
                messages.success(request, "Question added to the Question Bank.")
                return redirect("teacher_question_bank")
    return render(request, "assessments/teacher_question_form.html", {"form":form,"choice_formset":fs,"page_title":"Add New Question","submit_label":"Save Question"})

def teacher_question_edit(request, pk):
    q = get_object_or_404(Question, pk=pk, question_type__in=[Question.Type.MATHLIVE, Question.Type.MULTIPLE_CHOICE, Question.Type.MULTI_SELECT, Question.Type.YES_NO_MATRIX, Question.Type.GRID_LINE_DRAWING, Question.Type.EQUATION_BUILDER, Question.Type.NUMBER_LINE_DRAG, Question.Type.DRAG_DROP_IMAGE])
    form = TeacherQuestionForm(request.POST or None, instance=q)
    fs = _choice_formset(q, request.POST if request.method == "POST" else None)
    if request.method == "POST":
        fs_ok = fs.is_valid()
        if form.is_valid() and fs_ok:
            if form.cleaned_data["question_type"] not in [Question.Type.MULTIPLE_CHOICE, Question.Type.MULTI_SELECT, Question.Type.YES_NO_MATRIX] or _validate_mc(form, fs):
                _save_question(form, fs)
                messages.success(request, "Question updated.")
                return redirect("teacher_question_bank")
    return render(request, "assessments/teacher_question_form.html", {"form":form,"choice_formset":fs,"page_title":"Edit Question","submit_label":"Save Changes","question":q})

def teacher_question_delete(request, pk):
    q = get_object_or_404(Question, pk=pk, question_type__in=[Question.Type.MATHLIVE, Question.Type.MULTIPLE_CHOICE, Question.Type.MULTI_SELECT, Question.Type.YES_NO_MATRIX, Question.Type.GRID_LINE_DRAWING, Question.Type.EQUATION_BUILDER, Question.Type.NUMBER_LINE_DRAG, Question.Type.DRAG_DROP_IMAGE])
    if request.method == "POST":
        if q.questionsetitem_set.exists() or q.answer_set.exists():
            q.is_active = False
            q.save(update_fields=["is_active"])
            messages.info(request, "This question has assessment/history data, so it was archived instead of permanently deleted.")
        else:
            q.delete()
            messages.success(request, "Question deleted.")
        return redirect("teacher_question_bank")
    return render(request, "assessments/teacher_question_delete.html", {"question":q})


@ensure_csrf_cookie
def teacher_explain_set(request, public_id):
    question_set = get_object_or_404(
        QuestionSet.objects.prefetch_related(
            "items__question__choices",
            "items__question__free_annotations",
        ),
        public_id=public_id,
    )
    items = list(question_set.items.all())
    return render(request, "assessments/teacher_explain_set.html", {
        "question_set": question_set,
        "items": items,
    })


@require_POST
def teacher_free_annotation_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        payload = json.loads(request.body.decode("utf-8"))
        text = str(payload.get("text", "")).strip()
        x = max(0.0, min(1.0, float(payload.get("x", 0.5))))
        y = max(0.0, min(1.0, float(payload.get("y", 0.5))))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid annotation data."}, status=400)
    if not text:
        return JsonResponse({"ok": False, "error": "Annotation text cannot be blank."}, status=400)
    note = FreeAnnotation.objects.create(question=question, text=text, x=x, y=y)
    return JsonResponse({"ok": True, "id": note.id, "text": note.text, "x": note.x, "y": note.y})


@require_POST
def teacher_free_annotation_update(request, annotation_id):
    note = get_object_or_404(FreeAnnotation, pk=annotation_id)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid annotation data."}, status=400)
    if "text" in payload:
        text = str(payload["text"]).strip()
        if not text:
            return JsonResponse({"ok": False, "error": "Annotation text cannot be blank."}, status=400)
        note.text = text
    if "x" in payload:
        note.x = max(0.0, min(1.0, float(payload["x"])))
    if "y" in payload:
        note.y = max(0.0, min(1.0, float(payload["y"])))
    note.save()
    return JsonResponse({"ok": True, "id": note.id, "text": note.text, "x": note.x, "y": note.y})


@require_POST
def teacher_free_annotation_delete(request, annotation_id):
    note = get_object_or_404(FreeAnnotation, pk=annotation_id)
    note.delete()
    return JsonResponse({"ok": True})

def normalize_numeric(value):
    cleaned = value.strip().replace("\\cdot", "*").replace(" ", "")
    # Accept plain numbers and simple decimal strings for this prototype.
    if re.fullmatch(r"[-+]?\d+(\.\d+)?", cleaned):
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None
    return None


def answer_is_correct(question, submitted):
    if question.question_type == Question.Type.NUMBER_LINE_DRAG:
        try:
            payload = json.loads(submitted)
            expected = json.loads(question.correct_answer or "{}")
            return payload == expected
        except (TypeError, json.JSONDecodeError, AttributeError):
            return False
    if question.question_type == Question.Type.EQUATION_BUILDER:
        try:
            payload = json.loads(submitted)
            expected = json.loads(question.correct_answer or "{}")
            return payload == expected
        except (TypeError, json.JSONDecodeError, AttributeError):
            return False
    if question.question_type == Question.Type.GRID_LINE_DRAWING:
        # Open-response drawing item: preserve the vector answer for teacher review.
        # It is intentionally not auto-scored yet.
        try:
            payload = json.loads(submitted)
            return False if not payload.get("lines") else False
        except (TypeError, json.JSONDecodeError, AttributeError):
            return False
    if question.question_type == Question.Type.YES_NO_MATRIX:
        try:
            submitted_values = json.loads(submitted)
            expected_values = json.loads(question.correct_answer or "{}")
            normalized = {str(k): str(v).lower() == "yes" for k, v in submitted_values.items()}
            expected = {str(k): bool(v) for k, v in expected_values.items()}
            return normalized == expected
        except (TypeError, json.JSONDecodeError, AttributeError):
            return False
    if question.question_type == Question.Type.MULTI_SELECT:
        try:
            submitted_values = json.loads(submitted)
            expected_values = json.loads(question.correct_answer or "[]")
            return sorted(submitted_values) == sorted(expected_values)
        except (TypeError, json.JSONDecodeError):
            return False
    if question.question_type == Question.Type.DRAG_DROP_IMAGE:
        try:
            placements = json.loads(submitted)
        except (TypeError, json.JSONDecodeError):
            return False
        expected = question.drag_config.get("correct", {})
        return placements == expected
    if question.question_type == Question.Type.MATHLIVE:
        submitted_number = normalize_numeric(submitted)
        correct_number = normalize_numeric(question.correct_answer)
        if submitted_number is not None and correct_number is not None:
            return submitted_number == correct_number
    return submitted.strip().lower() == question.correct_answer.strip().lower()


def student_take_set(request, public_id):
    question_set = get_object_or_404(
        QuestionSet.objects.prefetch_related("items__question__choices"),
        public_id=public_id,
    )
    items = list(question_set.items.all())

    if request.method == "POST":
        student_name = request.POST.get("student_name", "").strip()
        if not student_name:
            messages.error(request, "Please enter your name.")
            return render(request, "assessments/student_take_set.html", {"question_set": question_set, "items": items})

        missing = [item.question.id for item in items if not request.POST.get(f"answer_{item.question.id}", "").strip()]
        if missing:
            messages.error(request, "Please answer every question before submitting.")
            return render(request, "assessments/student_take_set.html", {"question_set": question_set, "items": items})

        with transaction.atomic():
            submission = Submission.objects.create(question_set=question_set, student_name=student_name)
            for item in items:
                question = item.question
                value = request.POST.get(f"answer_{question.id}", "").strip()
                Answer.objects.create(
                    submission=submission,
                    question=question,
                    answer_text=value,
                    is_correct=answer_is_correct(question, value),
                )
        return redirect("submission_complete", submission_id=submission.id)

    return render(request, "assessments/student_take_set.html", {"question_set": question_set, "items": items})


def submission_complete(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("question_set"),
        id=submission_id,
    )
    return render(request, "assessments/submission_complete.html", {
        "submission": submission,
    })


@require_POST
def teacher_delete_set(request, public_id):
    question_set = get_object_or_404(QuestionSet, public_id=public_id)
    question_set.delete()
    return redirect("home")


def teacher_set_results(request, public_id):
    question_set = get_object_or_404(
        QuestionSet.objects.prefetch_related(
            "items__question",
            "submissions__answers__question",
        ),
        public_id=public_id,
    )
    submissions = list(question_set.submissions.all().order_by("-submitted_at"))
    rows = []
    for submission in submissions:
        answers = list(submission.answers.all())
        rows.append({
            "submission": submission,
            "answers": answers,
            "score": sum(answer.is_correct for answer in answers),
            "total": len(answers),
        })
    return render(request, "assessments/teacher_set_results.html", {
        "question_set": question_set,
        "rows": rows,
    })
