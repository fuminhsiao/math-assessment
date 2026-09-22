from django import forms
from django.forms import inlineformset_factory
from .models import Choice, Question, QuestionSet

class QuestionSetCreateForm(forms.Form):
    title = forms.CharField(label="Question set title", max_length=200, initial="Grade 6 Sample Question Set")
    questions = forms.ModelMultipleChoiceField(label="Select questions", queryset=Question.objects.none(), widget=forms.CheckboxSelectMultiple)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["questions"].queryset = Question.objects.filter(
            is_active=True,
            question_type__in=[Question.Type.MATHLIVE, Question.Type.MULTIPLE_CHOICE],
        ).prefetch_related("choices")
    def save(self):
        question_set = QuestionSet.objects.create(title=self.cleaned_data["title"])
        for index, question in enumerate(self.cleaned_data["questions"]):
            question_set.items.create(question=question, order=index)
        return question_set

class TeacherQuestionForm(forms.ModelForm):
    question_type = forms.ChoiceField(label="Question Type", choices=[
        (Question.Type.MATHLIVE, "Value Input"),
        (Question.Type.MULTIPLE_CHOICE, "Multiple Choice"),
    ])
    class Meta:
        model = Question
        fields = ["question_type", "prompt", "general_annotation", "correct_answer", "is_active"]
        labels = {"prompt":"Question Text","general_annotation":"General Annotation","correct_answer":"Correct Answer","is_active":"Available in Question Bank"}
        widgets = {
             "prompt": forms.Textarea(attrs={"rows":5,"placeholder":"Enter the question text students will see."}),
            "general_annotation": forms.Textarea(attrs={"rows":3,"placeholder":"Optional teacher note for the whole question."}),
            "correct_answer": forms.TextInput(attrs={"placeholder":"Example: 36.8","autocomplete":"off"}),
        }
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
