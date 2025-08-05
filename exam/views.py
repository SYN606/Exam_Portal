from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random

from .models import Exam, Question, Participant, ParticipantAnswer
from .forms import ParticipantForm

def home(request):
    exams = Exam.objects.filter(visible=True)
    return render(request, 'exam/home.html', {'exams': exams})


def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            mobile = form.cleaned_data['mobile']

            # ✅ Reuse participant if already exists
            participant, created = Participant.objects.get_or_create(
                name=name, mobile=mobile, exam=exam
            )

            if created:
                # New participant: shuffle and save question order
                questions = list(Question.objects.filter(exam=exam))
                random.shuffle(questions)
                for q in questions:
                    ParticipantAnswer.objects.get_or_create(participant=participant, question=q)
            else:
                # Existing participant: use stored question order
                questions = [
                    a.question for a in ParticipantAnswer.objects
                    .filter(participant=participant).select_related('question')
                ]

            # ✅ Prepare question data
            question_data = [{
                'id': q.id,
                'text': q.text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
            } for q in questions]

            # ✅ Get saved answers to restore selected options
            saved_answers = {
                a.question.id: a.selected_option
                for a in ParticipantAnswer.objects.filter(participant=participant)
                if a.selected_option
            }

            return render(request, 'exam/exam_page.html', {
                'exam': exam,
                'questions': question_data,
                'participant_id': participant.id,
                'duration_minutes': exam.duration,
                'saved_answers': saved_answers
            })
    else:
        form = ParticipantForm()

    return render(request, 'exam/participant_form.html', {
        'form': form,
        'exam': exam
    })


@csrf_exempt
@require_http_methods(["POST"])
def submit_exam(request):
    data = json.loads(request.body)
    answers = data.get("answers", {})
    participant_id = data.get("participant_id")

    try:
        participant = Participant.objects.get(id=participant_id)
        answers_qs = ParticipantAnswer.objects.filter(participant=participant).select_related('question')
    except Participant.DoesNotExist:
        return JsonResponse({"error": "Participant not found"}, status=400)

    score = 0
    attempted = 0
    detailed_results = []

    for idx, answer_obj in enumerate(answers_qs):
        question = answer_obj.question
        user_answer = answers.get(str(idx))  # index from frontend

        if user_answer:
            attempted += 1
            answer_obj.selected_option = user_answer
            answer_obj.save()

        correct = (user_answer == question.correct_option)
        if correct:
            score += 1

        detailed_results.append({
            "question": question.text,
            "your_answer": user_answer,
            "correct_answer": question.correct_option,
            "is_correct": correct
        })

    participant.score = score
    participant.save()

    return JsonResponse({
        "message": "Exam submitted successfully",
        "total": len(answers_qs),
        "attempted": attempted,
        "correct": score,
        "wrong": len(answers_qs) - score,
        "details": detailed_results
    })


# ✅ NEW: Save individual answer (used in AJAX call from exam_page.html)
@csrf_exempt
@require_http_methods(["POST"])
def save_answer(request):
    try:
        data = json.loads(request.body)
        participant_id = data.get("participant_id")
        question_id = data.get("question_id")
        selected_option = data.get("selected_option")

        participant = Participant.objects.get(id=participant_id)
        question = Question.objects.get(id=question_id)

        answer_obj, created = ParticipantAnswer.objects.get_or_create(
            participant=participant, question=question
        )
        answer_obj.selected_option = selected_option
        answer_obj.save()

        return JsonResponse({"message": "Answer saved successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
