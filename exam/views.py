from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.utils import timezone
from django.contrib import messages

import json

from .models import Exam, Question, Participant, ParticipantAnswer, Option


def home(request):
    if request.user.is_authenticated:
        exams = Exam.objects.filter(is_active=True).order_by("-created_at")
        return render(request, "exam/home.html", {"exams": exams})
    else:
        messages.error(request, "Please login first before attempting exams!")
        return redirect("home:login")


def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id, is_active=True)
    now = timezone.now()

    if exam.start_time and now < exam.start_time:
        return render(request, "exam/not_started.html", {"exam": exam})

    if exam.end_time and now > exam.end_time:
        return render(request, "exam/ended.html", {"exam": exam})

    if not request.user.is_authenticated:
        messages.error(request, "Please login first!")
        return redirect("home:login")

    participant, created = Participant.objects.get_or_create(
        user=request.user,
        exam=exam,
    )

    if created or not participant.started_at:
        participant.started_at = timezone.now()
        participant.save(update_fields=["started_at"])

    if participant.is_submitted:
        return render(request, "exam/already_submitted.html", {"exam": exam})

    questions = Question.objects.filter(exam=exam).prefetch_related("options")

    if created or not ParticipantAnswer.objects.filter(participant=participant).exists():
        ParticipantAnswer.objects.bulk_create(
            [
                ParticipantAnswer(participant=participant, question=q)
                for q in questions
            ],
            ignore_conflicts=True,
        )

    elapsed = (timezone.now() - participant.started_at).total_seconds()
    remaining_seconds = max(0, exam.duration * 60 - int(elapsed))

    # ✅ ONLY CHANGE: replace render with message + redirect
    if remaining_seconds <= 0:
        participant.is_submitted = True
        participant.submitted_at = timezone.now()
        participant.save(update_fields=["is_submitted", "submitted_at"])

        messages.error(request, "Time is up! Your exam has been submitted.")
        return redirect("exam:result_page", participant_id=participant.id)

    saved_answers = dict(
        ParticipantAnswer.objects.filter(
            participant=participant,
            selected_option__isnull=False
        ).values_list("question_id", "selected_option_id")
    )

    questions_data = [
        {
            "id": q.id,
            "text": q.text,
            "order": q.order,
            "options": [
                {"id": opt.id, "text": opt.text}
                for opt in q.options.all()
            ],
        }
        for q in questions
    ]

    return render(
        request,
        "exam/exam_page.html",
        {
            "exam": exam,
            "questions_json": json.dumps(questions_data),
            "saved_answers": json.dumps(saved_answers),
            "participant_id": participant.id,
            "remaining_seconds": int(remaining_seconds),
        },
    )


@csrf_protect
@require_http_methods(["POST"])
def save_answer(request):
    try:
        data = json.loads(request.body)
        participant = Participant.objects.get(id=data.get("participant_id"), user=request.user)

        if participant.is_submitted:
            return JsonResponse({"error": "Exam already submitted"}, status=400)

        question = Question.objects.get(id=data.get("question_id"), exam=participant.exam)
        option = Option.objects.get(id=data.get("selected_option"), question=question)

        answer_obj, _ = ParticipantAnswer.objects.get_or_create(
            participant=participant,
            question=question
        )

        answer_obj.selected_option = option
        answer_obj.save(update_fields=["selected_option", "answered_at"])
        return JsonResponse({"message": "saved"})

    except Exception:
        return JsonResponse({"error": "Something went wrong"}, status=400)


@csrf_protect
@require_http_methods(["POST"])
@transaction.atomic
def submit_exam(request):
    try:
        data = json.loads(request.body)
        participant = Participant.objects.select_related("exam").get(
            id=data.get("participant_id"),
            user=request.user
        )

        if participant.is_submitted:
            return JsonResponse({"error": "Already submitted"}, status=400)

        elapsed = (timezone.now() - participant.started_at).total_seconds()

        # (optional but safe) handle timeout here too
        if elapsed > participant.exam.duration * 60:
            participant.is_submitted = True
            participant.submitted_at = timezone.now()
            participant.save(update_fields=["is_submitted", "submitted_at"])

            return JsonResponse({
                "error": "Time expired",
                "redirect_url": f"/exam/result/{participant.id}/"
            }, status=400)

        answers = data.get("answers", {})
        answer_qs = ParticipantAnswer.objects.select_for_update().filter(
            participant=participant
        ).select_related("question")

        score = 0
        attempted = 0

        for ans in answer_qs:
            selected_option_id = answers.get(str(ans.question.id))
            if not selected_option_id:
                continue

            try:
                option = Option.objects.get(id=selected_option_id, question=ans.question)
            except Option.DoesNotExist:
                continue

            attempted += 1
            ans.selected_option = option

            if option.is_correct:
                score += float(participant.exam.marks_per_question)
            else:
                score -= float(participant.exam.negative_marks)

        ParticipantAnswer.objects.bulk_update(answer_qs, ["selected_option"])

        participant.score = max(0, round(score, 2))
        participant.is_submitted = True
        participant.submitted_at = timezone.now()
        participant.save(update_fields=["score", "is_submitted", "submitted_at"])

        return JsonResponse({
            "message": "submitted",
            "score": participant.score,
            "attempted": attempted,
            "total": answer_qs.count(),
        })

    except Exception:
        return JsonResponse({"error": "Submission failed"}, status=400)


def result_page(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id, user=request.user)
    answers = participant.answers.select_related('question', 'selected_option').all()
    attempted_questions_count = answers.filter(selected_option__isnull=False).count()

    return render(request, "exam/result.html", {
        "participant": participant,
        "answers": answers,
        "attempted_questions_count": attempted_questions_count
    })