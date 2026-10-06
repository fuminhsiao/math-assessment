from django.db import migrations, models

def add_grid_question(apps, schema_editor):
    Question=apps.get_model("assessments","Question")
    if not Question.objects.filter(question_type="grid_line_drawing", prompt__startswith="Maya says").exists():
        Question.objects.create(
            prompt="Maya says that a rhombus cannot also be a rectangle.\n\nShow Maya that her statement is not true.\nDraw a rhombus that is also a rectangle.",
            question_type="grid_line_drawing", correct_answer="", order=6, is_active=True,
            drag_config={"grid_cols":20,"grid_rows":20,"snap":True,"min_lines":1},
        )

class Migration(migrations.Migration):
    dependencies=[("assessments","0006_yes_no_matrix")]
    operations=[
        migrations.AlterField(model_name="question",name="question_type",field=models.CharField(choices=[("mathlive","MathLive response"),("multiple_choice","Multiple choice"),("multi_select","Multi-select"),("yes_no_matrix","Yes / No Matrix"),("grid_line_drawing","Grid Line Drawing"),("drag_drop_image","Drag and drop on image")],max_length=30,verbose_name="Question type")),
        migrations.RunPython(add_grid_question,migrations.RunPython.noop),
    ]
