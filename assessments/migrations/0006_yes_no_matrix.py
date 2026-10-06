import json
from django.db import migrations, models

def add_sample(apps, schema_editor):
    Question=apps.get_model("assessments","Question")
    Choice=apps.get_model("assessments","Choice")
    q=Question.objects.filter(question_type="yes_no_matrix", prompt__startswith="Does replacing the unknown number").first()
    if q: return
    q=Question.objects.create(prompt="Does replacing the unknown number with 7 make each equation true? Select Yes or No for each equation.",question_type="yes_no_matrix",order=5,is_active=True)
    rows=[("6 × □ = 36",False),("8 × □ = 64",False),("49 ÷ □ = 7",True),("54 ÷ □ = 6",False)]
    expected={}
    for i,(text,yes) in enumerate(rows,1):
        value=f"row_{i}"; Choice.objects.create(question=q,text=text,value=value,order=i); expected[value]=yes
    q.correct_answer=json.dumps(expected); q.save(update_fields=["correct_answer"])

class Migration(migrations.Migration):
    dependencies=[("assessments","0005_multi_select")]
    operations=[
      migrations.AlterField(model_name="question",name="question_type",field=models.CharField(choices=[("mathlive","MathLive response"),("multiple_choice","Multiple choice"),("multi_select","Multi-select"),("yes_no_matrix","Yes / No Matrix"),("drag_drop_image","Drag and drop on image")],max_length=30,verbose_name="Question type")),
      migrations.RunPython(add_sample,migrations.RunPython.noop),
    ]
