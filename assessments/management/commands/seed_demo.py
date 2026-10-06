import json
from django.core.management.base import BaseCommand
from assessments.models import Answer, Choice, Question, QuestionSet, Submission

class Command(BaseCommand):
    help = "Reset demo data and create exactly one question of each supported type."

    def handle(self, *args, **options):
        # Demo reset: remove old sets/submissions first so protected question references are gone.
        Answer.objects.all().delete()
        Submission.objects.all().delete()
        QuestionSet.objects.all().delete()
        Question.objects.all().delete()

        q1 = Question.objects.create(
            prompt="Enter the value of the expression: 2.3 · (4 + 12)",
            question_type=Question.Type.MATHLIVE,
            correct_answer="36.8", order=1, is_active=True,
        )

        q2 = Question.objects.create(
            prompt="Which value is equal to 1 1/2 + (-1/2)?",
            question_type=Question.Type.MULTIPLE_CHOICE,
            correct_answer="1", order=2, is_active=True,
        )
        for i, text in enumerate(["-2","-1","0","1"], 1):
            Choice.objects.create(question=q2, text=text, value=text, order=i)

        q3 = Question.objects.create(
            prompt="Move each ordered pair into the correct quadrant on the grid.",
            question_type=Question.Type.DRAG_DROP_IMAGE,
            correct_answer="", order=3, is_active=True,
            drag_config={
                "image":"assessments/coordinate-plane.svg",
                "choices":[
                    {"id":"neg_neg","label":"(−2, −1)"},{"id":"neg_pos","label":"(−2, 1)"},
                    {"id":"pos_neg","label":"(2, −1)"},{"id":"pos_pos","label":"(2, 1)"}],
                "correct":{"neg_neg":"q3","neg_pos":"q2","pos_neg":"q4","pos_pos":"q1"},
            },
        )

        q4 = Question.objects.create(
            prompt="Select all the expressions that are equivalent to 8(t + 4).",
            question_type=Question.Type.MULTI_SELECT,
            correct_answer=json.dumps(["choice_2","choice_5"]),
            order=4, is_active=True,
        )
        choices=[
            "2(4t + 2)",
            "8t + 32",
            "4t + 4 + 4t",
            "(8 + t) + (8 + 4)",
            "(8 × t) + (8 × 4)",
        ]
        for i,text in enumerate(choices,1):
            Choice.objects.create(question=q4, text=text, value=f"choice_{i}", order=i)

        q5 = Question.objects.create(
            prompt="Does replacing the unknown number with 7 make each equation true? Select Yes or No for each equation.",
            question_type=Question.Type.YES_NO_MATRIX, order=5, is_active=True,
        )
        matrix_rows=[("6 × □ = 36",False),("8 × □ = 64",False),("49 ÷ □ = 7",True),("54 ÷ □ = 6",False)]
        expected={}
        for i,(text,yes) in enumerate(matrix_rows,1):
            value=f"row_{i}"
            Choice.objects.create(question=q5,text=text,value=value,order=i)
            expected[value]=yes
        q5.correct_answer=json.dumps(expected)
        q5.save(update_fields=["correct_answer"])

        Question.objects.create(
            prompt="Maya says that a rhombus cannot also be a rectangle.\n\nShow Maya that her statement is not true.\nDraw a rhombus that is also a rectangle.",
            question_type=Question.Type.GRID_LINE_DRAWING, order=6, is_active=True,
            drag_config={"grid_cols":20,"grid_rows":20,"snap":True,"min_lines":1},
        )

        self.stdout.write(self.style.SUCCESS(
            "Question Bank reset: 6 questions created, including Grid Line Drawing."
        ))
