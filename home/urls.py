from django.urls import path
from .views import (
    HomePageView,
    AboutView,
    ContactView,
    RegisterView,
    LoginView,
    LogoutView,
    SecurityResetPasswordView,
)

app_name = 'home'

urlpatterns = [
    path('', HomePageView.as_view(), name='homepage'),
    path('about/', AboutView.as_view(), name='about-us'),
    path('contact/', ContactView.as_view(), name='contact-us'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset-password/', SecurityResetPasswordView.as_view(), name='reset-password'),
]