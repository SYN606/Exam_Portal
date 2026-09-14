from .auth import LoginView, LogoutView, RegisterView, SecurityResetPasswordView
from .base import AboutView, ContactView, FAQView, HomePageView, custom_404_view
from .student import StudentDashboardView, StudentExamDetailView, StudentExamHistoryView

__all__ = [
    "HomePageView",
    "AboutView",
    "ContactView",
    "FAQView",
    "StudentDashboardView",
    "StudentExamDetailView",
    "StudentExamHistoryView",
    "RegisterView",
    "LoginView",
    "LogoutView",
    "SecurityResetPasswordView",
    "custom_404_view"
]