import json
from django.db import migrations, models

def reset_question_bank(apps, schema_editor):
    Question = apps.get_model("assessments", "Question")
    Choice = apps.get_model("assessments", "Choice")
    QuestionSet = apps.get_model("assessments", "QuestionSet")
    Submission = apps.get_model("assessments", "Submission")
    Answer = apps.get_model("assessments", "Answer")

    # User-requested reset: old assessment history/sets must be removed first
    # because QuestionSetItem/Answer protect referenced questions.
    Answer.objects.all().delete()
    Submission.objects.all().delete()
    QuestionSet.objects.all().delete()
    Question.objects.all().delete()

    Question.objects.create(
        prompt="Enter the value of the expression: 2.3 · (4 + 12)",
        question_type="mathlive", correct_answer="36.8", order=1, is_active=True,
    )

    q2 = Question.objects.create(
        prompt="Which value is equal to 1 1/2 + (-1/2)?",
        question_type="multiple_choice", correct_answer="1", order=2, is_active=True,
    )
    for i, text in enumerate(["-2", "-1", "0", "1"], 1):
        Choice.objects.create(question=q2, text=text, value=text, order=i)

    Question.objects.create(
        prompt="Move each ordered pair into the correct quadrant on the grid.",
        question_type="drag_drop_image", correct_answer="", order=3, is_active=True,
        drag_config={
            "image": "assessments/coordinate-plane.svg",
            "choices": [
                {"id":"neg_neg","label":"(−2, −1)"},
                {"id":"neg_pos","label":"(−2, 1)"},
                {"id":"pos_neg","label":"(2, −1)"},
                {"id":"pos_pos","label":"(2, 1)"},
            ],
            "correct":{"neg_neg":"q3","neg_pos":"q2","pos_neg":"q4","pos_pos":"q1"},
        },
    )

    q4 = Question.objects.create(
        prompt="Select all the expressions that are equivalent to 8(t + 4).",
        question_type="multi_select",
        correct_answer=json.dumps(["choice_2", "choice_5"]),
        order=4, is_active=True,
    )
    for i, text in enumerate([
        "2(4t + 2)",
        "8t + 32",
        "4t + 4 + 4t",
        "(8 + t) + (8 + 4)",
        "(8 × t) + (8 × 4)",
    ], 1):
        Choice.objects.create(question=q4, text=text, value=f"choice_{i}", order=i)

class Migration(migrations.Migration):
    dependencies = [("assessments", "0004_teacher_annotations")]
    operations = [
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("mathlive","MathLive response"),
                    ("multiple_choice","Multiple choice"),
                    ("multi_select","Multi-select"),
                    ("drag_drop_image","Drag and drop on image"),
                ],
                max_length=30,
                verbose_name="Question type",
            ),
        ),
        migrations.RunPython(reset_question_bank, migrations.RunPython.noop),
    ]
