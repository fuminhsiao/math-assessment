import uuid
from django.db import models


class Question(models.Model):
    class Type(models.TextChoices):
        MATHLIVE = "mathlive", "MathLive response"
        MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
        DRAG_DROP_IMAGE = "drag_drop_image", "Drag and drop on image"

    prompt = models.TextField("Question prompt")
    question_type = models.CharField("Question type", max_length=30, choices=Type.choices)
    correct_answer = models.CharField("Correct answer", max_length=255, blank=True)
    order = models.PositiveIntegerField("Display order", default=0)
    is_active = models.BooleanField("Active", default=True)
    drag_config = models.JSONField("Drag-and-drop configuration", default=dict, blank=True, help_text="Zones, choices, and correct placements for drag-and-drop image questions.")

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.prompt[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField("Choice text", max_length=255)
    value = models.CharField("Stored value", max_length=100)
    order = models.PositiveIntegerField("Display order", default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class QuestionSet(models.Model):
    title = models.CharField("Question set title", max_length=200)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    questions = models.ManyToManyField(Question, through="QuestionSetItem")
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    def __str__(self):
        return self.title


class QuestionSetItem(models.Model):
    question_set = models.ForeignKey(QuestionSet, related_name="items", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    order = models.PositiveIntegerField("Display order", default=0)

    class Meta:
        ordering = ["order", "id"]
        constraints = [models.UniqueConstraint(fields=["question_set", "question"], name="unique_question_in_set")]


class Submission(models.Model):
    question_set = models.ForeignKey(QuestionSet, related_name="submissions", on_delete=models.CASCADE)
    student_name = models.CharField("Student name", max_length=120)
    submitted_at = models.DateTimeField("Submitted at", auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.question_set.title}"


class Answer(models.Model):
    submission = models.ForeignKey(Submission, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    answer_text = models.TextField("Student answer", blank=True)
    is_correct = models.BooleanField("Correct", default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["submission", "question"], name="one_answer_per_question")]
