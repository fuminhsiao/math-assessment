from django.db import migrations, models

def seed_map(apps, schema_editor):
    Question = apps.get_model("assessments", "Question")
    if not Question.objects.filter(subject="math_map", question_type="map_image_choice", prompt="Which picture shows the correct change?").exists():
        Question.objects.create(subject="math_map", question_type="map_image_choice", prompt="Which picture shows the correct change?", correct_answer="B", is_active=True, drag_config={"directions":"Use the information to answer the question.","description":"Manuel paid 34¢ for gum. He gave the clerk $1.","images":{}})

class Migration(migrations.Migration):
    dependencies = [("assessments", "0011_reading_types")]
    operations = [migrations.AlterField(model_name="question",name="subject",field=models.CharField(choices=[("math","Math (M-TEST)"),("math_map","Math (MAP)"),("english","English (M-TEST)")],default="math",max_length=20,verbose_name="Subject")),migrations.AlterField(model_name="question",name="question_type",field=models.CharField(choices=[("map_image_choice","MAP Image Choice (A–E)"),("mathlive","MathLive response"),("multiple_choice","Multiple choice"),("multi_select","Multi-select"),("yes_no_matrix","Yes / No Matrix"),("grid_line_drawing","Grid Line Drawing"),("equation_builder","Equation Builder"),("number_line_drag","Number Line Drag"),("drag_drop_image","Drag and drop on image"),("passage_sentence_select","Passage Sentence Select"),("passage_event_order","Reading Event Sequencing"),("passage_choice","Reading Multiple Choice"),("passage_multi","Reading Multiple Select"),("passage_two_part","Passage Two-Part")],max_length=30,verbose_name="Question type")),migrations.RunPython(seed_map,migrations.RunPython.noop)]
