import json
from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView, ListView

from .models import Exam, Option, Participant, ParticipantAnswer, Question


class HomeView(ListView):
    """Lists all active exams for authenticated users."""

    model = Exam
    template_name = "exam/home.html"
    context_object_name = "exams"

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            messages.error(request,
                           "Please login first before attempting exams!")
            return redirect("home:login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Exam.objects.filter(is_active=True).order_by("-created_at")


class StartExamView(LoginRequiredMixin, View):
    """Initializes exam sessions and renders the active exam page."""

    login_url = "home:login"

    def get(self, request: HttpRequest, exam_id: int) -> HttpResponse:
        exam = get_object_or_404(Exam, pk=exam_id, is_active=True)
        now = timezone.now()

        if exam.start_time and now < exam.start_time:
            return render(request, "exam/not_started.html", {"exam": exam})

        if exam.end_time and now > exam.end_time:
            return render(request, "exam/ended.html", {"exam": exam})

        participant, created = Participant.objects.get_or_create(
            user=request.user, exam=exam)

        if created or not participant.started_at:
            participant.started_at = timezone.now()
            participant.save(update_fields=["started_at"])

        if participant.is_submitted:
            return render(request, "exam/already_submitted.html",
                          {"exam": exam})

        questions = Question.objects.filter(
            exam=exam).prefetch_related("options")

        if (created or not ParticipantAnswer.objects.filter(
                participant=participant).exists()):
            ParticipantAnswer.objects.bulk_create([
                ParticipantAnswer(participant=participant, question=q)
                for q in questions
            ],
                                                  ignore_conflicts=True)

        elapsed = (timezone.now() - participant.started_at).total_seconds()
        remaining_seconds = max(0, exam.duration * 60 - int(elapsed))

        if remaining_seconds <= 0:
            participant.is_submitted = True
            participant.submitted_at = timezone.now()
            participant.save(update_fields=["is_submitted", "submitted_at"])

            messages.error(request,
                           "Time is up! Your exam has been submitted.")
            return redirect("exam:result_page", participant_id=participant.pk)

        saved_answers = dict(
            ParticipantAnswer.objects.filter(
                participant=participant,
                selected_option__isnull=False).values_list(
                    "question_id", "selected_option_id"))

        questions_data = [{
            "id":
            q.pk,
            "text":
            q.text,
            "order":
            q.order,
            "options": [{
                "id": opt.pk,
                "text": opt.text
            } for opt in q.options.all()],
        } for q in questions]

        return render(
            request, "exam/exam_page.html", {
                "exam": exam,
                "questions_json": json.dumps(questions_data),
                "saved_answers": json.dumps(saved_answers),
                "participant_id": participant.pk,
                "remaining_seconds": int(remaining_seconds),
            })


@method_decorator(csrf_protect, name="dispatch")
class SaveAnswerView(LoginRequiredMixin, View):
    """AJAX endpoint to auto-save single question answers as the student progresses."""

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data = json.loads(request.body)
            participant = Participant.objects.get(
                id=data.get("participant_id"), user=request.user)

            if participant.is_submitted:
                return JsonResponse({"error": "Exam already submitted"},
                                    status=400)

            question = Question.objects.get(id=data.get("question_id"),
                                            exam=participant.exam)
            option = Option.objects.get(id=data.get("selected_option"),
                                        question=question)

            answer_obj, _ = ParticipantAnswer.objects.get_or_create(
                participant=participant, question=question)

            answer_obj.selected_option = option
            answer_obj.save(update_fields=["selected_option", "answered_at"])
            return JsonResponse({"message": "saved"})

        except Exception:
            return JsonResponse({"error": "Something went wrong"}, status=400)


@method_decorator(csrf_protect, name="dispatch")
class SubmitExamView(LoginRequiredMixin, View):
    """AJAX endpoint to evaluate and finalize full exam submissions."""

    @transaction.atomic
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data = json.loads(request.body)
            participant = Participant.objects.select_related("exam").get(
                id=data.get("participant_id"), user=request.user)

            if participant.is_submitted:
                return JsonResponse({"error": "Already submitted"}, status=400)

            elapsed = (timezone.now() - participant.started_at).total_seconds()

            if elapsed > participant.exam.duration * 60:
                participant.is_submitted = True
                participant.submitted_at = timezone.now()
                participant.save(
                    update_fields=["is_submitted", "submitted_at"])

                return JsonResponse(
                    {
                        "error": "Time expired",
                        "redirect_url": f"/exam/result/{participant.pk}/",
                    },
                    status=400,
                )

            answers = data.get("answers", {})
            answer_qs = (ParticipantAnswer.objects.select_for_update().filter(
                participant=participant).select_related("question"))

            score = 0.0
            attempted = 0

            for ans in answer_qs:
                selected_option_id = answers.get(str(ans.question.pk))
                if not selected_option_id:
                    continue

                try:
                    option = Option.objects.get(id=selected_option_id,
                                                question=ans.question)
                except Option.DoesNotExist:
                    continue

                attempted += 1
                ans.selected_option = option

                if option.is_correct:
                    score += float(participant.exam.marks_per_question)
                else:
                    score -= float(participant.exam.negative_marks)

            ParticipantAnswer.objects.bulk_update(answer_qs,
                                                  ["selected_option"])

            participant.score = max(0.0, round(score, 2))
            participant.is_submitted = True
            participant.submitted_at = timezone.now()
            participant.save(
                update_fields=["score", "is_submitted", "submitted_at"])

            return JsonResponse({
                "message": "submitted",
                "score": participant.score,
                "attempted": attempted,
                "total": answer_qs.count(),
            })

        except Exception:
            return JsonResponse({"error": "Submission failed"}, status=400)


class ResultPageView(LoginRequiredMixin, DetailView):
    """Displays exam results and breakdown for a given participant."""

    model = Participant
    template_name = "exam/result.html"
    context_object_name = "participant"
    pk_url_kwarg = "participant_id"

    def get_queryset(self):
        return Participant.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        participant = cast(Participant, context["participant"])
        answers = participant.answers.select_related("question",
                                                     "selected_option").all()
        context["answers"] = answers
        context["attempted_questions_count"] = answers.filter(
            selected_option__isnull=False).count()
        return context
