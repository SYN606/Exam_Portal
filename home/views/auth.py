from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages

from home.models import User
from home.forms import LoginForm, RegisterForm, ResetPasswordStep1Form, ResetPasswordStep2Form


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        return render(request, self.template_name, {
            "questions": User.SecurityQuestion.choices
        })

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Student account created successfully! Please login.")
            return redirect("home:login")

        # Report all validation errors via messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

        context = {
            "questions": User.SecurityQuestion.choices,
            "form_data": {
                "username": request.POST.get("username", "").strip(),
                "email": request.POST.get("email", "").strip(),
                "security_question": request.POST.get("security_question", ""),
                "security_answer": request.POST.get("security_answer", "").strip(),
            }
        }
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        form = LoginForm(request.POST)
        username = request.POST.get("username", "").strip()

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("home:homepage")

        messages.error(request, "Invalid username or password")
        return render(request, self.template_name, {"username": username})


class LogoutView(View):
    def post(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
            messages.success(request, "You've been logged out successfully")
        return redirect("home:homepage")

    def get(self, request):
        messages.warning(request, "Logout must be submitted via a POST request.")
        return redirect("home:homepage")


class SecurityResetPasswordView(View):
    template_name = "reset_password.html"

    def get(self, request):
        if request.user.is_authenticated:
            messages.warning(request,
                             "Log out first to perform a password reset.")
            return redirect("home:homepage")
        return render(request, self.template_name, {"step": 1})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        step = request.POST.get("step")

        # STEP 1: Verify username and check for security setup
        if step == "1":
            form = ResetPasswordStep1Form(request.POST)
            if not form.is_valid():
                messages.error(request, "Please enter a valid username.")
                return render(request, self.template_name, {"step": 1})

            username = form.cleaned_data["username"].strip()
            user = User.objects.filter(username=username).first()

            if not user or not user.security_question:
                messages.error(request, "Account not found or password recovery is not configured for this user.")
                return render(request, self.template_name, {
                    "step": 1,
                    "username": username
                })

            question_label = user.get_security_question_display()
            return render(
                request, self.template_name, {
                    "step": 2,
                    "username": username,
                    "question_display": question_label
                })

        # STEP 2: Validate security answer and process new password
        elif step == "2":
            username = request.POST.get("username", "").strip()
            user = User.objects.filter(username=username).first()
            question_label = (user.get_security_question_display()
                              if user and user.security_question else "")

            form = ResetPasswordStep2Form(request.POST)
            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                return render(
                    request, self.template_name, {
                        "step": 2,
                        "username": username,
                        "question_display": question_label
                    })

            if not user:
                messages.error(request, "An error occurred. Please try again.")
                return redirect("home:login")

            security_answer = form.cleaned_data["security_answer"]
            new_password = form.cleaned_data["new_password"]

            if user.check_security_answer(security_answer):
                user.set_password(new_password)
                user.save()
                messages.success(
                    request,
                    "Password reset successfully! You can now log in.")
                return redirect("home:login")
            else:
                messages.error(request, "Incorrect security answer.")
                return render(
                    request, self.template_name, {
                        "step": 2,
                        "username": username,
                        "question_display": question_label
                    })

        return redirect("home:login")
