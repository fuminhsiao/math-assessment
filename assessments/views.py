import json
import re
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import QuestionSetCreateForm
from .models import Answer, Question, QuestionSet, Submission


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
