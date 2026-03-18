from django.urls import path
from . import views

app_name = "exam"

urlpatterns = [
    path("", views.home, name="exam_list"),  # /exams/
    path("<int:exam_id>/", views.start_exam, name="start_exam"),
    # API
    path("api/submit/", views.submit_exam, name="submit_exam"),
    path("api/save-answer/", views.save_answer, name="save_answer"),
]
