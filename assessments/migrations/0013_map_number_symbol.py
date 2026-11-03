from django.db import migrations, models

def add_sample(apps, schema_editor):
    Question = apps.get_model("assessments", "Question")
    prompt = "How much did Marshall pay in all? Move a number and a symbol to the lines to show the answer."
    if not Question.objects.filter(subject="math_map", question_type="map_number_symbol", prompt=prompt).exists():
        Question.objects.create(subject="math_map", question_type="map_number_symbol", prompt=prompt, correct_answer="17¢", is_active=True, drag_config={"directions":"Use the information to answer the question.","description":"Marshall buys a pencil for 12¢ and a sticker for 5¢. He has no money left over.","tokens":["12","13","14","15","16","17","18","19","$","¢"]})

class Migration(migrations.Migration):
    dependencies = [("assessments", "0012_map_question")]
    operations = [migrations.AlterField(model_name="question", name="question_type", field=models.CharField(choices=[("map_number_symbol", "MAP Number & Symbol Placement"), ("map_image_choice", "MAP Image Choice (A–E)"), ("mathlive", "MathLive response"), ("multiple_choice", "Multiple choice"), ("multi_select", "Multi-select"), ("yes_no_matrix", "Yes / No Matrix"), ("grid_line_drawing", "Grid Line Drawing"), ("equation_builder", "Equation Builder"), ("number_line_drag", "Number Line Drag"), ("drag_drop_image", "Drag and drop on image"), ("passage_sentence_select", "Passage Sentence Select"), ("passage_event_order", "Reading Event Sequencing"), ("passage_choice", "Reading Multiple Choice"), ("passage_multi", "Reading Multiple Select"), ("passage_two_part", "Passage Two-Part")], max_length=30, verbose_name="Question type")), migrations.RunPython(add_sample, migrations.RunPython.noop)]
