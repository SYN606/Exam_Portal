from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Sum
from django.views.generic import DetailView, ListView
from exam.models import Exam, Participant


class StudentDashboardView(LoginRequiredMixin, ListView):
    """Rich student dashboard showing overall metrics, performance trends, and exam history."""

    model = Participant
    template_name = "student_dashboard.html"
    context_object_name = "submitted_exams"

    def get_queryset(self):
        return (Participant.objects.filter(
            user=self.request.user,
            is_submitted=True
        ).select_related("exam").order_by("-submitted_at"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_submissions = self.get_queryset()

        stats = user_submissions.aggregate(
            total_exams=Count("id"),
            avg_score=Avg("score"),
            total_correct=Sum("total_correct"),
            total_wrong=Sum("total_wrong"),
            total_unanswered=Sum("total_unanswered"),
        )

        total_correct = stats["total_correct"] or 0
        total_wrong = stats["total_wrong"] or 0
        total_unanswered = stats["total_unanswered"] or 0
        total_attempted = total_correct + total_wrong
        total_questions_encountered = total_attempted + total_unanswered

        accuracy_rate = (
            round((total_correct / total_attempted) * 100, 1)
            if total_attempted > 0 else 0.0
        )
        avg_score = round(stats["avg_score"] or 0.0, 2)

        available_exams = Exam.objects.filter(is_active=True).order_by("-created_at")[:5]

        context["total_exams"] = stats["total_exams"] or 0
        context["avg_score"] = avg_score
        context["total_correct"] = total_correct
        context["total_wrong"] = total_wrong
        context["total_unanswered"] = total_unanswered
        context["total_attempted"] = total_attempted
        context["total_questions_encountered"] = total_questions_encountered
        context["accuracy_rate"] = accuracy_rate
        context["available_exams"] = available_exams

        return context


# Backward-compatible alias
StudentExamHistoryView = StudentDashboardView


class StudentExamDetailView(LoginRequiredMixin, DetailView):
    """Shows right and wrong answer breakdown, explanations, and question filtering."""

    model = Participant
    template_name = "exam_detail.html"
    context_object_name = "participant"
    pk_url_kwarg = "participant_id"

    def get_queryset(self):
        return Participant.objects.filter(user=self.request.user,
                                          is_submitted=True).select_related("exam")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participant = context["participant"]

        answers = (participant.answers.select_related(
            "question",
            "selected_option"
        ).prefetch_related("question__options").order_by("question__order", "id").all())

        total_questions = participant.exam.total_questions
        attempted = participant.total_correct + participant.total_wrong
        accuracy = (
            round((participant.total_correct / attempted) * 100, 1)
            if attempted > 0 else 0.0
        )
        score_percent = (
            round((participant.score / participant.exam.total_marks) * 100, 1)
            if participant.exam.total_marks > 0 else 0.0
        )

        context["answers"] = answers
        context["total_questions"] = total_questions
        context["attempted_questions"] = attempted
        context["accuracy"] = accuracy
        context["score_percent"] = score_percent
        return context

