from django.urls import path
from . import views

urlpatterns = [
    path("", views.superadmin_login, name="superAdminLogin"),
    path("dashboard/", views.superAdminDashboard, name="superAdminDashboard"),
]