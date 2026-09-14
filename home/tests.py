from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("home:register")
        self.login_url = reverse("home:login")
        self.logout_url = reverse("home:logout")
        self.reset_url = reverse("home:reset-password")

    def test_register_weak_password_rejected(self):
        """Weak password (too short / common) must be rejected by password validation."""
        response = self.client.post(self.register_url, {
            "username": "student_weak",
            "email": "student_weak@example.com",
            "security_question": User.SecurityQuestion.PET,
            "security_answer": "Fluffy",
            "password1": "123",
            "password2": "123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="student_weak").exists())

    def test_register_mismatched_passwords_rejected(self):
        """Mismatched passwords must be rejected."""
        response = self.client.post(self.register_url, {
            "username": "student_mismatch",
            "email": "mismatch@example.com",
            "security_question": User.SecurityQuestion.PET,
            "security_answer": "Fluffy",
            "password1": "ComplexPass123!@#",
            "password2": "DifferentPass123!@#",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="student_mismatch").exists())

    def test_register_valid_user_success(self):
        """Valid registration creates a STUDENT user with hashed security answer."""
        response = self.client.post(self.register_url, {
            "username": "student_valid",
            "email": "valid@example.com",
            "security_question": User.SecurityQuestion.PET,
            "security_answer": "Fluffy",
            "password1": "ComplexPass123!@#",
            "password2": "ComplexPass123!@#",
        })
        self.assertRedirects(response, self.login_url)
        user = User.objects.get(username="student_valid")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.check_security_answer("fluffy"))
        self.assertTrue(user.check_password("ComplexPass123!@#"))

    def test_logout_get_request_disallowed(self):
        """GET request to logout should not log out authenticated user and should issue a warning."""
        user = User.objects.create_user(
            username="testuser",
            password="ComplexPass123!@#",
            role=User.Role.STUDENT
        )
        self.client.login(username="testuser", password="ComplexPass123!@#")
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse("home:homepage"))
        # User is still authenticated in session
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_post_request_allowed(self):
        """POST request to logout successfully logs out the user."""
        user = User.objects.create_user(
            username="testuser2",
            password="ComplexPass123!@#",
            role=User.Role.STUDENT
        )
        self.client.login(username="testuser2", password="ComplexPass123!@#")
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, reverse("home:homepage"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_reset_password_workflow_and_validation(self):
        """Password reset verifies security answer and enforces password validation."""
        user = User.objects.create_user(
            username="reset_user",
            email="reset@example.com",
            password="OldPassword123!@#",
            role=User.Role.STUDENT
        )
        user.security_question = User.SecurityQuestion.CITY
        user.set_security_answer("Berlin")
        user.save()

        # Step 1: Request reset for username
        resp1 = self.client.post(self.reset_url, {
            "step": "1",
            "username": "reset_user"
        })
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.context["step"], 2)

        # Step 2: Try with weak password
        resp_weak = self.client.post(self.reset_url, {
            "step": "2",
            "username": "reset_user",
            "security_answer": "Berlin",
            "new_password": "123",
            "confirm_password": "123",
        })
        self.assertEqual(resp_weak.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("OldPassword123!@#"))

        # Step 2: Try with incorrect security answer
        resp_wrong_ans = self.client.post(self.reset_url, {
            "step": "2",
            "username": "reset_user",
            "security_answer": "WrongCity",
            "new_password": "NewComplexPass123!@#",
            "confirm_password": "NewComplexPass123!@#",
        })
        self.assertEqual(resp_wrong_ans.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("OldPassword123!@#"))

        # Step 2: Success with valid answer and complex password
        resp_success = self.client.post(self.reset_url, {
            "step": "2",
            "username": "reset_user",
            "security_answer": "berlin",
            "new_password": "NewComplexPass123!@#",
            "confirm_password": "NewComplexPass123!@#",
        })
        self.assertRedirects(resp_success, self.login_url)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewComplexPass123!@#"))


class StudentDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="dashboard_student",
            password="ComplexPass123!@#",
            role=User.Role.STUDENT
        )
        self.other_student = User.objects.create_user(
            username="other_student",
            password="ComplexPass123!@#",
            role=User.Role.STUDENT
        )
        self.teacher = User.objects.create_user(
            username="dash_teacher",
            password="ComplexPass123!@#",
            role=User.Role.TEACHER
        )

        from exam.models import Exam, Question, Option, Participant, ParticipantAnswer
        self.exam = Exam.objects.create(
            title="Science Assessment",
            duration=45,
            marks_per_question=5.0,
            negative_marks=1.0,
            created_by=self.teacher,
            is_active=True
        )

        self.q1 = Question.objects.create(
            exam=self.exam,
            text="What is H2O?",
            explanation="H2O is the chemical formula for water.",
            order=1
        )
        self.opt1_correct = Option.objects.create(question=self.q1, text="Water", is_correct=True)
        self.opt2_wrong = Option.objects.create(question=self.q1, text="Oxygen", is_correct=False)

        self.participant = Participant.objects.create(
            user=self.student,
            exam=self.exam,
            is_submitted=True,
            score=5.0,
            total_correct=1,
            total_wrong=0,
            total_unanswered=0
        )
        ParticipantAnswer.objects.create(
            participant=self.participant,
            question=self.q1,
            selected_option=self.opt1_correct
        )

    def test_dashboard_requires_login(self):
        """Unauthenticated user is redirected to login."""
        dashboard_url = reverse("home:student-dashboard")
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_kpis_and_history_rendered(self):
        """Authenticated student sees their completed exams, accuracy, and score stats."""
        self.client.login(username="dashboard_student", password="ComplexPass123!@#")
        dashboard_url = reverse("home:student-dashboard")
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Science Assessment")
        self.assertEqual(response.context["total_exams"], 1)
        self.assertEqual(response.context["total_correct"], 1)
        self.assertEqual(response.context["accuracy_rate"], 100.0)

    def test_exam_detail_explanations_rendered(self):
        """Student exam review displays question text, explanation, and correct answer badge."""
        self.client.login(username="dashboard_student", password="ComplexPass123!@#")
        detail_url = reverse("home:exam-detail", kwargs={"participant_id": self.participant.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What is H2O?")
        self.assertContains(response, "H2O is the chemical formula for water.")
        self.assertContains(response, "Correct")

    def test_student_cannot_view_another_students_exam_detail(self):
        """A student cannot access another student's exam review page."""
        self.client.login(username="other_student", password="ComplexPass123!@#")
        detail_url = reverse("home:exam-detail", kwargs={"participant_id": self.participant.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)


