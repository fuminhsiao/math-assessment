from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("assessments", "0002_replace_desmos_with_mathlive")]
    operations = [
        migrations.AddField(
            model_name="question",
            name="drag_config",
            field=models.JSONField(blank=True, default=dict, help_text="Zones, choices, and correct placements for drag-and-drop image questions.", verbose_name="Drag-and-drop configuration"),
        ),
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(choices=[("mathlive", "MathLive response"), ("multiple_choice", "Multiple choice"), ("drag_drop_image", "Drag and drop on image")], max_length=30, verbose_name="Question type"),
        ),
    ]
