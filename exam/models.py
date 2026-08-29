from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    marks_per_question = models.FloatField(default=1.0)
    negative_marks = models.FloatField(default=0.0)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_exams",
        limit_choices_to={'role__in': ['ADMIN', 'TEACHER']},
        null=True,
        blank=True)

    is_active = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        questions: models.Manager["Question"]
        participants: models.Manager["Participant"]

    def __str__(self):
        return self.title

    @property
    def total_questions(self) -> int:
        return self.questions.count()

    @property
    def total_marks(self) -> float:
        return self.total_questions * self.marks_per_question


class Question(models.Model):
    exam = models.ForeignKey(Exam,
                             on_delete=models.CASCADE,
                             related_name="questions")
    text = models.TextField()
    explanation = models.TextField(
        blank=True, help_text="Explanation for the correct answer")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        options: models.Manager["Option"]

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.pk} - {self.text[:50]}"


class Option(models.Model):
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Participant(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="participants")
    exam = models.ForeignKey(Exam,
                             on_delete=models.CASCADE,
                             related_name="participants")

    score = models.FloatField(default=0.0)
    total_correct = models.PositiveIntegerField(default=0)
    total_wrong = models.PositiveIntegerField(default=0)
    total_unanswered = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)

    if TYPE_CHECKING:
        answers: models.Manager["ParticipantAnswer"]

    class Meta:
        unique_together = ("user", "exam")
        indexes = [
            models.Index(fields=["user", "exam"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"

    def calculate_score(self):
        """Calculates score, correct, wrong, and unattempted metrics upon submission."""
        correct = 0
        wrong = 0

        answers = self.answers.select_related("selected_option")
        all_questions_count = self.exam.questions.count()
        answered_q_ids = set(answers.values_list("question_id", flat=True))

        for answer in answers:
            if answer.selected_option and answer.selected_option.is_correct:
                correct += 1
            elif answer.selected_option:
                wrong += 1

        unanswered = max(0, all_questions_count - len(answered_q_ids))

        self.total_correct = correct
        self.total_wrong = wrong
        self.total_unanswered = unanswered
        self.score = (correct * self.exam.marks_per_question) - (
            wrong * self.exam.negative_marks)
        self.save()


class ParticipantAnswer(models.Model):
    question_id: int
    participant = models.ForeignKey(Participant,
                                    on_delete=models.CASCADE,
                                    related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        blank=True)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("participant", "question")
        indexes = [
            models.Index(fields=["participant", "question"]),
        ]

    @property
    def is_correct(self) -> bool:
        return bool(self.selected_option and self.selected_option.is_correct)

    def __str__(self):
        return f"{self.participant} - Q{self.question_id}"
