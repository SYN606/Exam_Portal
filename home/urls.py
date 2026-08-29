from django.urls import path
from .views import (
    HomePageView,
    AboutView,
    ContactView,
    FAQView,  # Added missing view
    RegisterView,
    LoginView,
    LogoutView,
    SecurityResetPasswordView,
    StudentExamHistoryView,
    StudentExamDetailView,
)

app_name = "home"

urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
    path("about/", AboutView.as_view(), name="about-us"),
    path("contact/", ContactView.as_view(), name="contact-us"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "reset-password/",
        SecurityResetPasswordView.as_view(),
        name="reset-password",
    ),
    # Student Exam Backtracking Routes
    path("my-history/", StudentExamHistoryView.as_view(), name="exam-history"),
    path(
        "my-history/<int:participant_id>/",
        StudentExamDetailView.as_view(),
        name="exam-detail",
    ),
]
