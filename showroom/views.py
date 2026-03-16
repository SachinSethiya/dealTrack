from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
def login_view(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")

User = get_user_model()

def signup(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )
        return redirect("login")
    return render(request, "signup.html")

@login_required
def dashboard(request):
    return render(request,"dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("login")