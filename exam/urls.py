from django.urls import path

from .views import (
    HomeView,
    ResultPageView,
    SaveAnswerView,
    StartExamView,
    SubmitExamView,
)

app_name = "exam"

urlpatterns = [
    # Exam List / Homepage (/exam/)
    path("", HomeView.as_view(), name="exam_list"),
    # Start/Active Exam Page (/exam/1/)
    path("<int:exam_id>/", StartExamView.as_view(), name="start_exam"),
    # Exam Results Page (/exam/result/1/)
    path("result/<int:participant_id>/",
         ResultPageView.as_view(),
         name="result_page"),
    # AJAX Endpoints
    path("api/save-answer/", SaveAnswerView.as_view(), name="save_answer"),
    path("api/submit/", SubmitExamView.as_view(), name="submit_exam"),
]
