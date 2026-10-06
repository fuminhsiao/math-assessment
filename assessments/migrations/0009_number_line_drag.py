import json
from django.db import migrations, models

def add_demo(apps, schema_editor):
    Question=apps.get_model("assessments","Question")
    prompt="Drag each fraction to the correct location on the number line."
    if Question.objects.filter(question_type="number_line_drag", prompt=prompt).exists(): return
    positions=[str(x/4).rstrip('0').rstrip('.') if x%4 else str(x//4) for x in range(17)]
    config={
      "min":0,"max":4,"step":0.25,"positions":positions,
      "choices":[
        {"value":"4/1","n":"4","d":"1"},
        {"value":"1/4","n":"1","d":"4"},
        {"value":"2/4","n":"2","d":"4"},
        {"value":"4/4","n":"4","d":"4"},
      ]
    }
    expected={"4/1":"4","1/4":"0.25","2/4":"0.5","4/4":"1"}
    order=(Question.objects.order_by('-order').values_list('order',flat=True).first() or 0)+1
    Question.objects.create(prompt=prompt,question_type="number_line_drag",correct_answer=json.dumps(expected),drag_config=config,order=order,is_active=True)

class Migration(migrations.Migration):
    dependencies=[("assessments","0008_equation_builder")]
    operations=[
      migrations.AlterField(model_name="question",name="question_type",field=models.CharField(choices=[("mathlive","MathLive response"),("multiple_choice","Multiple choice"),("multi_select","Multi-select"),("yes_no_matrix","Yes / No Matrix"),("grid_line_drawing","Grid Line Drawing"),("equation_builder","Equation Builder"),("number_line_drag","Number Line Drag"),("drag_drop_image","Drag and drop on image")],max_length=30,verbose_name="Question type")),
      migrations.RunPython(add_demo,migrations.RunPython.noop),
    ]
