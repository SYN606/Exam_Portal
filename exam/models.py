from django.db import models
from django.contrib.auth.models import User

# =======================
# EXAM
# =======================
class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    marks_per_question = models.FloatField(default=1)
    negative_marks = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()


# =======================
# QUESTION
# =======================
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.id} - {self.text[:50]}"


# =======================
# OPTION
# =======================
class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# =======================
# PARTICIPANT
# =======================
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="participants")

    score = models.FloatField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "exam")
        indexes = [
            models.Index(fields=["user", "exam"]),
        ]

    def __str__(self):
        return f"{self.user.username}"


# =======================
# PARTICIPANT ANSWER
# =======================
class ParticipantAnswer(models.Model):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.ForeignKey(
        Option, on_delete=models.CASCADE, null=True, blank=True
    )
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("participant", "question")
        indexes = [
            models.Index(fields=["participant", "question"]),
        ]

    def __str__(self):
        return f"{self.participant} - Q{self.question.id}"