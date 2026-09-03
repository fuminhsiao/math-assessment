from django.test import TestCase
from django.urls import reverse
from .models import Choice, Question, QuestionSet, QuestionSetItem, Submission


class AssessmentFlowTests(TestCase):
    def setUp(self):
        self.mathlive = Question.objects.create(prompt="2.3*(4+12)", question_type="mathlive", correct_answer="36.8")
        self.mcq = Question.objects.create(prompt="1.5 + -0.5", question_type="multiple_choice", correct_answer="1")
        Choice.objects.create(question=self.mcq, text="1", value="1")
        self.question_set = QuestionSet.objects.create(title="Test")
        QuestionSetItem.objects.create(question_set=self.question_set, question=self.mathlive, order=0)
        QuestionSetItem.objects.create(question_set=self.question_set, question=self.mcq, order=1)

    def test_teacher_can_create_set(self):
        response = self.client.post(reverse("teacher_create_set"), {
            "title": "New set",
            "questions": [self.mathlive.id, self.mcq.id],
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(QuestionSet.objects.filter(title="New set").exists())

    def test_student_submission_creates_answers(self):
        response = self.client.post(reverse("student_take_set", args=[self.question_set.public_id]), {
            "student_name": "Student A",
            f"answer_{self.mathlive.id}": "36.8",
            f"answer_{self.mcq.id}": "1",
        })
        self.assertEqual(response.status_code, 302)
        submission = Submission.objects.get()
        self.assertEqual(submission.answers.filter(is_correct=True).count(), 2)


    def test_teacher_home_lists_created_sets_and_links_to_results(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question_set.title)
        self.assertContains(
            response,
            reverse("teacher_set_results", args=[self.question_set.public_id]),
        )
