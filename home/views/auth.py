from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages

from home.models import User


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        return render(request, self.template_name,
                      {"questions": User.SecurityQuestion.choices})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        question = request.POST.get("security_question", "")
        answer = request.POST.get("security_answer", "").strip()

        context = {
            "questions": User.SecurityQuestion.choices,
            "form_data": {
                "username": username,
                "email": email,
                "security_question": question,
                "security_answer": answer
            }
        }

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, self.template_name, context)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, self.template_name, context)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, self.template_name, context)

        if not question or not answer:
            messages.error(request,
                           "Security question and answer are required!")
            return render(request, self.template_name, context)

        # Enforce STUDENT role strictly for public registrations
        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password1,
                                        role=User.Role.STUDENT)
        user.security_question = question
        user.set_security_answer(answer)
        user.save()

        messages.success(
            request, "Student account created successfully! Please login.")
        return redirect("home:login")


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home:homepage")

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home:homepage")

        messages.error(request, "Invalid username or password")
        return render(request, self.template_name, {"username": username})


class LogoutView(View):

    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
            messages.success(request, "You've been logged out successfully")
        return redirect("home:homepage")

    def post(self, request):
        return self.get(request)


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
            username = request.POST.get("username", "").strip()
            try:
                user = User.objects.get(username=username)
                if not user.security_question:
                    messages.error(request,
                                   "No security question set for this user.")
                    return render(request, self.template_name, {"step": 1})

                question_label = getattr(user,
                                         "get_security_question_display")()

                return render(
                    request, self.template_name, {
                        "step": 2,
                        "username": username,
                        "question_display": question_label
                    })
            except User.DoesNotExist:
                messages.error(request, "Username not found.")
                return render(request, self.template_name, {
                    "step": 1,
                    "username": username
                })

        # STEP 2: Validate security answer and process new password
        elif step == "2":
            username = request.POST.get("username", "").strip()
            answer = request.POST.get("security_answer", "").strip()
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            try:
                user = User.objects.get(username=username)
                question_label = getattr(user,
                                         "get_security_question_display")()

                if new_password != confirm_password:
                    messages.error(request, "Passwords do not match!")
                    return render(
                        request, self.template_name, {
                            "step": 2,
                            "username": username,
                            "question_display": question_label
                        })

                if user.check_security_answer(answer):
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
            except User.DoesNotExist:
                messages.error(request, "An error occurred. Please try again.")
                return redirect("home:login")

        return redirect("home:login")
