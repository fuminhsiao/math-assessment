import json
from django.db import migrations, models

def add_demo(apps, schema_editor):
    Question=apps.get_model("assessments","Question")
    if Question.objects.filter(question_type="equation_builder", prompt__startswith="Christy has $60").exists(): return
    config={
      "operators":["+","−","×","÷"],
      "numbers":["18","19","23","37","41","60","102"],
      "slots":["number","operator","number","operator","number","number"],
      "plants":[["grapevines","Grapevines, $16"],["apple","Apple tree, $18"],["pear","Pear tree, $20"]]
    }
    expected={"slots":["60","−","23","−","19","18"],"plant":"grapevines"}
    Question.objects.create(
      prompt="Christy has $60 to spend on plants.\nShe buys a peach tree for $23 and a plum tree for $19.\n\nShe wants to buy one more plant.\n\n• Drag the numbers to the boxes and the symbols to the circles to create an equation to show how much money Christy has left to spend.\n\n• Select one plant she could buy with the money she has left.",
      question_type="equation_builder", correct_answer=json.dumps(expected), drag_config=config, order=7, is_active=True)

class Migration(migrations.Migration):
    dependencies=[("assessments","0007_grid_line_drawing")]
    operations=[
      migrations.AlterField(model_name="question",name="question_type",field=models.CharField(choices=[("mathlive","MathLive response"),("multiple_choice","Multiple choice"),("multi_select","Multi-select"),("yes_no_matrix","Yes / No Matrix"),("grid_line_drawing","Grid Line Drawing"),("equation_builder","Equation Builder"),("drag_drop_image","Drag and drop on image")],max_length=30,verbose_name="Question type")),
      migrations.RunPython(add_demo,migrations.RunPython.noop),
    ]
