from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login , logout as auth_logout , authenticate 
from django.contrib import messages 


def homepage(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # ✅ Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "register.html")

        # ✅ Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "register.html")

        # ✅ Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "register.html")

        # ✅ Create user properly (password is hashed automatically)
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect("home:login")

    return render(request, "register.html")



def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request , username = username , password = password)

        if user is not None:
            auth_login(request,user)
            messages.success(request , f"Welcome back , {user.username} !")
            return redirect("home:homepage")
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "login.html")
    else:
        return render(request , "login.html")


def logout(request):
    auth_logout(request)
    messages.success(request , "You've been logged out successfully")
    return redirect("home:homepage")
