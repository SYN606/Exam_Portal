from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.utils import timezone

import json

from .models import Exam, Question, Participant, ParticipantAnswer, Option
from .forms import ParticipantForm


def home(request):
    exams = Exam.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "exam/home.html", {"exams": exams})


def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id, is_active=True)

    now = timezone.now()

    if exam.start_time and now < exam.start_time:
        return render(request, "exam/not_started.html", {"exam": exam})

    if exam.end_time and now > exam.end_time:
        return render(request, "exam/ended.html", {"exam": exam})

    if request.method == "POST":
        form = ParticipantForm(request.POST, exam=exam)

        if form.is_valid():
            mobile = form.cleaned_data["mobile"]
            name = form.cleaned_data["name"]

            participant, created = Participant.objects.get_or_create(
                mobile=mobile,
                exam=exam,
                defaults={"name": name},
            )

            if participant.is_submitted:
                return render(request, "exam/already_submitted.html", {"exam": exam})

            questions = (
                Question.objects.filter(exam=exam)
                .prefetch_related("options")
                .order_by("order")
            )

            # Create answers only first time
            if created:
                ParticipantAnswer.objects.bulk_create(
                    [
                        ParticipantAnswer(participant=participant, question=q)
                        for q in questions
                    ],
                    ignore_conflicts=True,
                )

            # ======================
            # TIMER LOGIC (IMPORTANT)
            # ======================
            elapsed = (timezone.now() - participant.started_at).total_seconds()
            remaining_seconds = max(0, exam.duration * 60 - int(elapsed))

            # If time already expired → force submit state
            if remaining_seconds <= 0:
                participant.is_submitted = True
                participant.submitted_at = timezone.now()
                participant.save(update_fields=["is_submitted", "submitted_at"])

                return render(request, "exam/time_up.html", {"exam": exam})

            # ======================
            # RESUME ANSWERS
            # ======================
            saved_answers = dict(
                ParticipantAnswer.objects.filter(
                    participant=participant, selected_option__isnull=False
                ).values_list("question_id", "selected_option_id")
            )

            questions_data = [
                {
                    "id": q.id,
                    "text": q.text,
                    "options": [
                        {"id": opt.id, "text": opt.text} for opt in q.options.all()
                    ],
                }
                for q in questions
            ]

            return render(
                request,
                "exam/exam_page.html",
                {
                    "exam": exam,
                    "questions": questions,
                    "questions_json": json.dumps(questions_data),
                    "saved_answers": json.dumps(saved_answers),
                    "participant_id": participant.id,
                    "remaining_seconds": int(remaining_seconds),  # ✅ KEY
                },
            )

    else:
        form = ParticipantForm(exam=exam)

    return render(request, "exam/participant_form.html", {"form": form, "exam": exam})


@csrf_protect
@require_http_methods(["POST"])
def save_answer(request):
    try:
        data = json.loads(request.body)

        participant = Participant.objects.select_related("exam").get(
            id=data.get("participant_id")
        )

        if participant.is_submitted:
            return JsonResponse({"error": "Exam already submitted"}, status=400)

        question = Question.objects.get(
            id=data.get("question_id"), exam=participant.exam
        )

        option = Option.objects.get(id=data.get("selected_option"), question=question)

        answer_obj, _ = ParticipantAnswer.objects.get_or_create(
            participant=participant, question=question
        )

        answer_obj.selected_option = option
        answer_obj.save(update_fields=["selected_option", "answered_at"])

        return JsonResponse({"message": "saved"})

    except Participant.DoesNotExist, Question.DoesNotExist, Option.DoesNotExist:
        return JsonResponse({"error": "Invalid data"}, status=400)

    except Exception:
        return JsonResponse({"error": "Something went wrong"}, status=400)


@csrf_protect
@require_http_methods(["POST"])
@transaction.atomic
def submit_exam(request):
    try:
        data = json.loads(request.body)

        participant = Participant.objects.select_related("exam").get(
            id=data.get("participant_id")
        )

        if participant.is_submitted:
            return JsonResponse({"error": "Already submitted"}, status=400)

        # ======================
        # TIMER VALIDATION (ANTI-CHEAT)
        # ======================
        elapsed = (timezone.now() - participant.started_at).total_seconds()

        if elapsed > participant.exam.duration * 60:
            participant.is_submitted = True
            participant.submitted_at = timezone.now()
            participant.save(update_fields=["is_submitted", "submitted_at"])

            return JsonResponse({"error": "Time expired"}, status=400)

        answers = data.get("answers", {})

        if not isinstance(answers, dict):
            return JsonResponse({"error": "Invalid answers format"}, status=400)

        answer_qs = (
            ParticipantAnswer.objects.select_for_update()
            .filter(participant=participant)
            .select_related("question")
            .prefetch_related("question__options")
        )

        score = 0
        attempted = 0

        for ans in answer_qs:
            selected_option_id = answers.get(str(ans.question.id))

            if not selected_option_id:
                continue

            option = next(
                (
                    opt
                    for opt in ans.question.options.all()
                    if str(opt.id) == str(selected_option_id)
                ),
                None,
            )

            if not option:
                continue

            attempted += 1
            ans.selected_option = option

            if option.is_correct:
                score += participant.exam.marks_per_question
            else:
                score -= participant.exam.negative_marks

        ParticipantAnswer.objects.bulk_update(answer_qs, ["selected_option"])

        participant.score = max(0, round(score, 2))
        participant.is_submitted = True
        participant.submitted_at = timezone.now()
        participant.save(update_fields=["score", "is_submitted", "submitted_at"])

        return JsonResponse(
            {
                "message": "submitted",
                "score": participant.score,
                "attempted": attempted,
                "total": answer_qs.count(),
            }
        )

    except Participant.DoesNotExist:
        return JsonResponse({"error": "Invalid participant"}, status=400)

    except Exception:
        return JsonResponse({"error": "Submission failed"}, status=400)
