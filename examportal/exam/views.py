from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random

from .models import Exam, Question, Participant
from .forms import ParticipantForm

def home(request):
    # ✅ Show only visible exams
    exams = Exam.objects.filter(visible=True)
    return render(request, 'exam/home.html', {'exams': exams})


def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.exam = exam
            participant.save()

            # ✅ Get and shuffle questions
            questions = list(Question.objects.filter(exam=exam).values())
            random.shuffle(questions)

            # ✅ Save order in session to match during submit
            request.session[f"exam_{participant.id}_questions"] = [q['id'] for q in questions]

            return render(request, 'exam/exam_page.html', {
                'exam': exam,
                'questions': questions,
                'participant_id': participant.id,
                'duration_minutes': exam.duration
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
    exam_id = data.get("exam_id")
    participant_id = data.get("participant_id")

    try:
        exam = Exam.objects.get(id=exam_id)
        question_ids = request.session.get(f"exam_{participant_id}_questions", [])
        questions = list(Question.objects.filter(id__in=question_ids))
    except Exam.DoesNotExist:
        return JsonResponse({"error": "Invalid exam ID"}, status=400)

    # Rebuild question dict for lookup by ID
    question_dict = {str(q.id): q for q in questions}

    score = 0
    detailed_results = []

    for index, qid in enumerate(question_ids):
        q = question_dict.get(str(qid))
        if q:
            user_answer = answers.get(str(index))
            correct = (user_answer == q.correct_option)
            if correct:
                score += 1
            detailed_results.append({
                "question": q.text,
                "your_answer": user_answer,
                "correct_answer": q.correct_option,
                "is_correct": correct
            })

    # ✅ Update participant score
    try:
        participant = Participant.objects.get(id=participant_id)
        participant.score = score
        participant.save()
    except Participant.DoesNotExist:
        return JsonResponse({"error": "Participant not found"}, status=400)

    return JsonResponse({
        "message": "Exam submitted successfully",
        "total": len(questions),
        "correct": score,
        "wrong": len(questions) - score,
        "details": detailed_results
    })
