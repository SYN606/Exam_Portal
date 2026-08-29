from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from exam.models import Participant


class StudentExamHistoryView(LoginRequiredMixin, ListView):
    """Lists all exams completed by the logged-in student."""

    model = Participant
    template_name = "exam_history.html"
    context_object_name = "submitted_exams"

    def get_queryset(self):
        return (Participant.objects.filter(
            user=self.request.user,
            is_submitted=True).select_related("exam").order_by("-submitted_at")
                )


class StudentExamDetailView(LoginRequiredMixin, DetailView):
    """Shows right and wrong answer breakdown for a specific submitted exam."""

    model = Participant
    template_name = "exam_detail.html"
    context_object_name = "participant"
    pk_url_kwarg = "participant_id"

    def get_queryset(self):
        return Participant.objects.filter(user=self.request.user,
                                          is_submitted=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participant = context["participant"]

        answers = (participant.answers.select_related(
            "question",
            "selected_option").prefetch_related("question__options").all())

        context["answers"] = answers
        return context
