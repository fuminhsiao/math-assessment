from django import forms
from django.forms import inlineformset_factory
from .models import Choice, Question, QuestionSet

class QuestionSetCreateForm(forms.Form):
    title = forms.CharField(label="Question set title", max_length=200, initial="", required=False)
    questions = forms.ModelMultipleChoiceField(label="Select questions", queryset=Question.objects.none(), widget=forms.CheckboxSelectMultiple)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["questions"].queryset = Question.objects.filter(
            is_active=True,
            question_type__in=[
                Question.Type.MATHLIVE,
                Question.Type.MULTIPLE_CHOICE,
                Question.Type.MULTI_SELECT,
                Question.Type.YES_NO_MATRIX,
                Question.Type.GRID_LINE_DRAWING,
                Question.Type.EQUATION_BUILDER,
                Question.Type.NUMBER_LINE_DRAG,
                Question.Type.DRAG_DROP_IMAGE,
                Question.Type.PASSAGE_SENTENCE_SELECT,
                Question.Type.PASSAGE_TWO_PART,
                Question.Type.PASSAGE_EVENT_ORDER,
                Question.Type.PASSAGE_CHOICE,
                Question.Type.PASSAGE_MULTI,
            ],
        ).prefetch_related("choices")
    def save(self):
        question_set = QuestionSet.objects.create(title=self.cleaned_data["title"])
        for index, question in enumerate(self.cleaned_data["questions"]):
            question_set.items.create(question=question, order=index)
        return question_set

class TeacherQuestionForm(forms.ModelForm):
    subject = forms.ChoiceField(label="Subject", choices=Question.Subject.choices)
    passage_text = forms.CharField(label="Passage", required=False, widget=forms.Textarea(attrs={"rows":12,"placeholder":"Paste the reading passage here."}))
    selectable_sentences = forms.CharField(label="Selectable sentences", required=False, widget=forms.Textarea(attrs={"rows":6,"placeholder":"One selectable sentence per line."}))
    part_a_prompt = forms.CharField(label="Part A prompt", required=False, widget=forms.Textarea(attrs={"rows":3}))
    part_b_prompt = forms.CharField(label="Part B prompt", required=False, widget=forms.Textarea(attrs={"rows":3}))
    part_a_choices = forms.CharField(label="Part A choices", required=False, widget=forms.Textarea(attrs={"rows":5,"placeholder":"One choice per line; prefix correct choice with *"}))
    part_b_choices = forms.CharField(label="Part B choices", required=False, widget=forms.Textarea(attrs={"rows":5,"placeholder":"One choice per line; prefix correct choice with *"}))
    question_type = forms.ChoiceField(label="Question Type", choices=[
        (Question.Type.MATHLIVE, "Value Input"),
        (Question.Type.MULTIPLE_CHOICE, "Multiple Choice"),
        (Question.Type.MULTI_SELECT, "Multi-select"),
        (Question.Type.YES_NO_MATRIX, "Yes / No Matrix"),
        (Question.Type.GRID_LINE_DRAWING, "Grid Line Drawing"),
        (Question.Type.EQUATION_BUILDER, "Equation Builder"),
        (Question.Type.NUMBER_LINE_DRAG, "Number Line Drag"),
        (Question.Type.DRAG_DROP_IMAGE, "Drag and Drop Image"),
        (Question.Type.PASSAGE_SENTENCE_SELECT, "Passage Sentence Select"),
        (Question.Type.PASSAGE_TWO_PART, "Passage Two-Part (A/B)"),
        (Question.Type.PASSAGE_EVENT_ORDER, "Reading Event Sequencing"),
        (Question.Type.PASSAGE_CHOICE, "Reading Multiple Choice"),
        (Question.Type.PASSAGE_MULTI, "Reading Multiple Select"),
    ])
    class Meta:
        model = Question
        fields = ["subject", "question_type", "prompt", "general_annotation", "correct_answer", "is_active"]
        labels = {"prompt":"Question Text","general_annotation":"General Annotation","correct_answer":"Correct Answer","is_active":"Available in Question Bank"}
        widgets = {
             "prompt": forms.Textarea(attrs={"rows":5,"placeholder":"Enter the question text students will see."}),
            "general_annotation": forms.Textarea(attrs={"rows":3,"placeholder":"Optional teacher note for the whole question."}),
            "correct_answer": forms.TextInput(attrs={"placeholder":"Example: 36.8","autocomplete":"off"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cfg = self.instance.drag_config or {} if self.instance and self.instance.pk else {}
        self.fields["passage_text"].initial = cfg.get("passage", "")
        
        try:
            correct_sentence_indexes = set(__import__("json").loads(self.instance.correct_answer or "[]")) if self.instance.question_type == Question.Type.PASSAGE_SENTENCE_SELECT else set()
        except Exception:
            correct_sentence_indexes = set()
        self.fields["selectable_sentences"].initial = "\n".join(("*" if i in correct_sentence_indexes else "") + x for i,x in enumerate(cfg.get("sentences", [])))
        self.fields["part_a_prompt"].initial = cfg.get("part_a", {}).get("prompt", "")
        self.fields["part_b_prompt"].initial = cfg.get("part_b", {}).get("prompt", "")
        def lines(part):
            out=[]
            for c in cfg.get(part, {}).get("choices", []): out.append(("*" if c.get("correct") else "") + c.get("text", ""))
            return "\n".join(out)
        self.fields["part_a_choices"].initial = lines("part_a")
        self.fields["part_b_choices"].initial = lines("part_b")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("question_type") == Question.Type.MATHLIVE and not (cleaned.get("correct_answer") or "").strip():
            self.add_error("correct_answer", "Enter the correct value.")
        return cleaned

class ChoiceForm(forms.ModelForm):
    is_correct = forms.BooleanField(required=False, label="Correct")
    class Meta:
        model = Choice
        fields = ["text", "annotation", "value", "order"]
        widgets = {"text":forms.TextInput(attrs={"placeholder":"Answer choice"}),"annotation":forms.TextInput(attrs={"placeholder":"Optional choice annotation"}),"value":forms.HiddenInput(),"order":forms.HiddenInput()}

ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=0, can_delete=True)
