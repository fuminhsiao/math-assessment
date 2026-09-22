from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("assessments", "0003_drag_drop_image")]
    operations = [
        migrations.AddField(model_name="question", name="general_annotation", field=models.TextField(blank=True, help_text="Optional note shown only on the teacher explanation page.", verbose_name="General teacher annotation")),
        migrations.AddField(model_name="choice", name="annotation", field=models.TextField(blank=True, help_text="Optional teacher-only explanation for this answer choice.", verbose_name="Choice annotation")),
        migrations.CreateModel(
            name="FreeAnnotation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(verbose_name="Annotation")),
                ("x", models.FloatField(verbose_name="Horizontal position")),
                ("y", models.FloatField(verbose_name="Vertical position")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="free_annotations", to="assessments.question")),
            ],
            options={"ordering":["id"]},
        ),
    ]
