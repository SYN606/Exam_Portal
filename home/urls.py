from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("about/", views.about, name="about-us"),
    path("contact/", views.contact, name="contact-us"),
    path("register/",views.register,name="register"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
]
