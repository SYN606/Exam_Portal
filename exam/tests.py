import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from exam.models import Exam, Question, Option, Participant, ParticipantAnswer

User = get_user_model()


class ExamLogicAndScoringTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="exam_taker",
            password="ComplexPass123!@#",
            role=User.Role.STUDENT
        )
        self.client.login(username="exam_taker", password="ComplexPass123!@#")

        # Create teacher and exam
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="ComplexPass123!@#",
            role=User.Role.TEACHER
        )
        self.exam = Exam.objects.create(
            title="Python Fundamentals",
            duration=30,
            marks_per_question=2.0,
            negative_marks=0.5,
            created_by=self.teacher,
            is_active=True
        )

        # Create 3 questions with options
        # Q1: Correct is Opt1
        self.q1 = Question.objects.create(exam=self.exam, text="What is Python?", order=1)
        self.opt1_q1 = Option.objects.create(question=self.q1, text="Programming Language", is_correct=True)
        self.opt2_q1 = Option.objects.create(question=self.q1, text="Snake", is_correct=False)

        # Q2: Correct is Opt1
        self.q2 = Question.objects.create(exam=self.exam, text="Is Python typed?", order=2)
        self.opt1_q2 = Option.objects.create(question=self.q2, text="Dynamically typed", is_correct=True)
        self.opt2_q2 = Option.objects.create(question=self.q2, text="Not typed", is_correct=False)

        # Q3: Correct is Opt1
        self.q3 = Question.objects.create(exam=self.exam, text="Keyword for functions?", order=3)
        self.opt1_q3 = Option.objects.create(question=self.q3, text="def", is_correct=True)
        self.opt2_q3 = Option.objects.create(question=self.q3, text="function", is_correct=False)

    def test_participant_calculate_score_direct(self):
        """Test Participant.calculate_score() accuracy for correct, wrong, and unanswered questions."""
        participant = Participant.objects.create(user=self.user, exam=self.exam)

        # Answer Q1 correctly
        ParticipantAnswer.objects.create(
            participant=participant,
            question=self.q1,
            selected_option=self.opt1_q1
        )
        # Answer Q2 incorrectly
        ParticipantAnswer.objects.create(
            participant=participant,
            question=self.q2,
            selected_option=self.opt2_q2
        )
        # Q3 left with no option selected (unanswered placeholder)
        ParticipantAnswer.objects.create(
            participant=participant,
            question=self.q3,
            selected_option=None
        )

        participant.calculate_score()
        participant.refresh_from_db()

        self.assertEqual(participant.total_correct, 1)
        self.assertEqual(participant.total_wrong, 1)
        self.assertEqual(participant.total_unanswered, 1)
        # Score = (1 * 2.0) - (1 * 0.5) = 1.5
        self.assertEqual(participant.score, 1.5)

    def test_start_exam_and_answer_flow(self):
        """Test starting exam, auto-saving answer, and final submission."""
        start_url = reverse("exam:start_exam", kwargs={"exam_id": self.exam.pk})
        response = self.client.get(start_url)
        self.assertEqual(response.status_code, 200)

        participant = Participant.objects.get(user=self.user, exam=self.exam)
        self.assertFalse(participant.is_submitted)
        self.assertEqual(ParticipantAnswer.objects.filter(participant=participant).count(), 3)

        # Save single answer via AJAX
        save_url = reverse("exam:save_answer")
        save_resp = self.client.post(
            save_url,
            data=json.dumps({
                "participant_id": participant.pk,
                "question_id": self.q1.pk,
                "selected_option": self.opt1_q1.pk
            }),
            content_type="application/json"
        )
        self.assertEqual(save_resp.status_code, 200)
        self.assertEqual(save_resp.json().get("message"), "saved")

        # Submit full exam via AJAX
        submit_url = reverse("exam:submit_exam")
        submit_resp = self.client.post(
            submit_url,
            data=json.dumps({
                "participant_id": participant.pk,
                "answers": {
                    str(self.q1.pk): self.opt1_q1.pk,   # correct: +2.0
                    str(self.q2.pk): self.opt2_q2.pk,   # wrong: -0.5
                    # Q3 not answered
                }
            }),
            content_type="application/json"
        )
        self.assertEqual(submit_resp.status_code, 200)
        data = submit_resp.json()
        self.assertEqual(data.get("message"), "submitted")
        self.assertEqual(data.get("score"), 1.5)
        self.assertEqual(data.get("attempted"), 2)

        participant.refresh_from_db()
        self.assertTrue(participant.is_submitted)
        self.assertEqual(participant.total_correct, 1)
        self.assertEqual(participant.total_wrong, 1)
        self.assertEqual(participant.total_unanswered, 1)
        self.assertEqual(participant.score, 1.5)

        # Verify Result Page loads and shows answers
        result_url = reverse("exam:result_page", kwargs={"participant_id": participant.pk})
        result_resp = self.client.get(result_url)
        self.assertEqual(result_resp.status_code, 200)
        self.assertContains(result_resp, "1.5")

    def test_auto_submit_with_suspicious_activity_reason(self):
        """Auto-submitting due to inspect mode or tab switch sets reason warning and submits exam."""
        participant = Participant.objects.create(user=self.user, exam=self.exam)
        ParticipantAnswer.objects.create(participant=participant, question=self.q1)
        ParticipantAnswer.objects.create(participant=participant, question=self.q2)
        ParticipantAnswer.objects.create(participant=participant, question=self.q3)

        submit_url = reverse("exam:submit_exam")
        reason_msg = "Developer tools / inspect mode shortcut detected."
        submit_resp = self.client.post(
            submit_url,
            data=json.dumps({
                "participant_id": participant.pk,
                "answers": {},
                "reason": reason_msg
            }),
            content_type="application/json"
        )
        self.assertEqual(submit_resp.status_code, 200)
        participant.refresh_from_db()
        self.assertTrue(participant.is_submitted)

        # Check that result page loads and shows the warning message
        result_url = reverse("exam:result_page", kwargs={"participant_id": participant.pk})
        result_resp = self.client.get(result_url)
        self.assertEqual(result_resp.status_code, 200)
        self.assertContains(result_resp, reason_msg)


