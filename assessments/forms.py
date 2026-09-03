from django import forms
from .models import Question, QuestionSet


class QuestionSetCreateForm(forms.Form):
    title = forms.CharField(label="Question set title", max_length=200, initial="Grade 7 Sample Question Set")
    questions = forms.ModelMultipleChoiceField(
        label="Select questions",
        queryset=Question.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["questions"].queryset = Question.objects.filter(is_active=True).prefetch_related("choices")

    def save(self):
        question_set = QuestionSet.objects.create(title=self.cleaned_data["title"])
        for index, question in enumerate(self.cleaned_data["questions"]):
            question_set.items.create(question=question, order=index)
        return question_set
