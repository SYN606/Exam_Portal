from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Exam, Question, Participant
from .forms import ParticipantForm

def home(request):
    exams = Exam.objects.all()
    return render(request, 'exam/home.html', {'exams': exams})


def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.exam = exam
            participant.save()

            questions = list(Question.objects.filter(exam=exam).values())
            return render(request, 'exam/exam_page.html', {
                'exam': exam,
                'questions': questions,
                'participant_id': participant.id
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

    exam = Exam.objects.get(id=exam_id)
    questions = Question.objects.filter(exam=exam)
    score = 0

    detailed_results = []

    for i, question in enumerate(questions):
        user_answer = answers.get(str(i))
        correct = (user_answer == question.correct_option)
        if correct:
            score += 1
        detailed_results.append({
            "question": question.text,
            "your_answer": user_answer,
            "correct_answer": question.correct_option,
            "is_correct": correct
        })

    
    if participant_id:
        try:
            participant = Participant.objects.get(id=participant_id)
            if hasattr(participant, 'score'):
                participant.score = score
                participant.save()
        except Participant.DoesNotExist:
            pass

    return JsonResponse({
        "message": "Exam submitted successfully",
        "total": len(questions),
        "correct": score,
        "wrong": len(questions) - score,
        "details": detailed_results
    })
