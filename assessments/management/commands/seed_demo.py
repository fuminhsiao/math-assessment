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

        # Keep the Render/PostgreSQL demo data in sync with the newer question types.
        Question.objects.create(
            prompt=(
                "Christy has $60 to spend on plants.\n"
                "She buys a peach tree for $23 and a plum tree for $19.\n\n"
                "She wants to buy one more plant.\n\n"
                "• Drag the numbers to the boxes and the symbols to the circles to create an equation "
                "to show how much money Christy has left to spend.\n\n"
                "• Select one plant she could buy with the money she has left."
            ),
            question_type=Question.Type.EQUATION_BUILDER,
            correct_answer=json.dumps({"slots":["60","−","23","−","19","18"],"plant":"grapevines"}),
            drag_config={
                "operators":["+","−","×","÷"],
                "numbers":["18","19","23","37","41","60","102"],
                "slots":["number","operator","number","operator","number","number"],
                "plants":[["grapevines","Grapevines, $16"],["apple","Apple tree, $18"],["pear","Pear tree, $20"]],
            },
            order=7, is_active=True,
        )

        Question.objects.create(
            prompt="Drag each fraction to the correct location on the number line.",
            question_type=Question.Type.NUMBER_LINE_DRAG,
            correct_answer=json.dumps({"4/1":"4","1/4":"0.25","2/4":"0.5","4/4":"1"}),
            drag_config={
                "min":0,"max":4,"step":0.25,
                "positions":[str(x/4).rstrip("0").rstrip(".") if x % 4 else str(x//4) for x in range(17)],
                "choices":[
                    {"value":"4/1","n":"4","d":"1"},
                    {"value":"1/4","n":"1","d":"4"},
                    {"value":"2/4","n":"2","d":"4"},
                    {"value":"4/4","n":"4","d":"4"},
                ],
            },
            order=8, is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(
            "Question Bank reset: 8 questions created, one for each supported demo type."
        ))
