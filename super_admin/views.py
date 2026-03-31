from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def superadmin_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("superAdminDashboard")

    return render(request, "super_admin/login.html")


@login_required
def superAdminDashboard(request):
    
    return render(request,"super_admin/dashboard.html")