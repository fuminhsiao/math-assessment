from django.core.management.base import BaseCommand

from assessments.models import Choice, Question, QuestionSet


class Command(BaseCommand):
    help = "Create demonstration assessment questions"

    def create_mathlive(self, prompt, answer, order):
        question, _ = Question.objects.update_or_create(
            prompt=prompt,
            defaults={
                "question_type": Question.Type.MATHLIVE,
                "correct_answer": answer,
                "order": order,
                "is_active": True,
            },
        )
        question.choices.all().delete()

    def create_multiple_choice(self, prompt, answer, choices, order):
        question, _ = Question.objects.update_or_create(
            prompt=prompt,
            defaults={
                "question_type": Question.Type.MULTIPLE_CHOICE,
                "correct_answer": answer,
                "order": order,
                "is_active": True,
            },
        )
        question.choices.all().delete()
        for choice_order, value in enumerate(choices, start=1):
            Choice.objects.create(
                question=question,
                text=str(value),
                value=str(value),
                order=choice_order,
            )


    def create_drag_drop(self, order):
        config = {
            "image": "assessments/coordinate-plane.svg",
            "choices": [
                {"id": "neg_neg", "label": "(−2, −1)"},
                {"id": "neg_pos", "label": "(−2, 1)"},
                {"id": "pos_neg", "label": "(2, −1)"},
                {"id": "pos_pos", "label": "(2, 1)"},
            ],
            "correct": {"neg_neg": "q3", "neg_pos": "q2", "pos_neg": "q4", "pos_pos": "q1"},
        }
        question, _ = Question.objects.update_or_create(
            prompt="Move each ordered pair into the correct quadrant on the grid.",
            defaults={
                "question_type": Question.Type.DRAG_DROP_IMAGE,
                "correct_answer": "",
                "drag_config": config,
                "order": order,
                "is_active": True,
            },
        )
        question.choices.all().delete()
        question_set, _ = QuestionSet.objects.get_or_create(title="Coordinate Quadrants – Drag and Drop")
        if not question_set.items.filter(question=question).exists():
            question_set.items.create(question=question, order=0)

    def handle(self, *args, **options):
        mathlive_questions = [
            ("Enter the value of the expression: 2.3 · (4 + 12)", "36.8"),
            ("Evaluate: 18 ÷ 3 + 7", "13"),
            ("Evaluate: 5² - 9", "16"),
            ("Solve for x: x + 8 = 21", "13"),
            ("Solve for x: 4x = 36", "9"),
            ("Find 3/4 of 20.", "15"),
            ("Evaluate: 6(3 + 2) - 4", "26"),
            ("Solve for x: 2x - 5 = 17", "11"),
        ]
        for order, (prompt, answer) in enumerate(mathlive_questions, start=1):
            self.create_mathlive(prompt, answer, order)

        multiple_choice_questions = [
            ("Which value is equal to 1 1/2 + (-1/2)?", "1", ["-2", "-1", "0", "1"]),
            ("Which number is the greatest?", "0.75", ["0.5", "0.65", "0.7", "0.75"]),
            ("Which expression is equal to 24?", "6 × 4", ["3 × 6", "6 × 4", "8 + 8", "30 - 4"]),
            ("What is the value of 7²?", "49", ["14", "21", "42", "49"]),
            ("Which fraction is equivalent to 1/2?", "4/8", ["2/3", "3/5", "4/8", "5/8"]),
            ("Which integer is farthest to the left on a number line?", "-8", ["-8", "-3", "0", "5"]),
            ("Which expression has a value of 15?", "3 × 5", ["10 + 2", "3 × 5", "20 - 3", "30 ÷ 3"]),
            ("Which decimal is equivalent to 3/5?", "0.6", ["0.3", "0.5", "0.6", "0.8"]),
        ]
        start_order = len(mathlive_questions) + 1
        for offset, (prompt, answer, choices) in enumerate(multiple_choice_questions):
            self.create_multiple_choice(prompt, answer, choices, start_order + offset)

        self.create_drag_drop(start_order + len(multiple_choice_questions))
        self.stdout.write(self.style.SUCCESS("Created or updated 17 demonstration questions, including drag and drop."))
