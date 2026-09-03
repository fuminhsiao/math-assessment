from django.db import migrations, models


def desmos_to_mathlive(apps, schema_editor):
    Question = apps.get_model("assessments", "Question")
    Question.objects.filter(question_type="desmos").update(question_type="mathlive")


def mathlive_to_desmos(apps, schema_editor):
    Question = apps.get_model("assessments", "Question")
    Question.objects.filter(question_type="mathlive").update(question_type="desmos")


class Migration(migrations.Migration):
    dependencies = [("assessments", "0001_initial")]

    operations = [
        migrations.RunPython(desmos_to_mathlive, mathlive_to_desmos),
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("mathlive", "MathLive response"),
                    ("multiple_choice", "Multiple choice"),
                ],
                max_length=30,
                verbose_name="Question type",
            ),
        ),
    ]
