from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("assessments", "0013_map_number_symbol")]
    operations = [migrations.AlterField(model_name="question", name="question_type", field=models.CharField(max_length=30, choices=[("map_array_input", "MAP Array Numeric Input"), ("map_number_symbol", "MAP Number & Symbol Placement"), ("map_image_choice", "MAP Image Choice (A–E)"), ("mathlive", "MathLive response"), ("multiple_choice", "Multiple choice"), ("multi_select", "Multi-select"), ("yes_no_matrix", "Yes / No Matrix"), ("grid_line_drawing", "Grid Line Drawing"), ("equation_builder", "Equation Builder"), ("number_line_drag", "Number Line Drag"), ("drag_drop_image", "Drag and drop on image"), ("passage_sentence_select", "Passage Sentence Select"), ("passage_event_order", "Reading Event Sequencing"), ("passage_choice", "Reading Multiple Choice"), ("passage_multi", "Reading Multiple Select"), ("passage_two_part", "Passage Two-Part")]))]
