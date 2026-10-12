from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("assessments", "0009_number_line_drag")]
    operations = [migrations.AddField(model_name="question", name="subject", field=models.CharField(choices=[("math","Mathematics"),("english","English Language Arts")], default="math", max_length=20, verbose_name="Subject"))]
