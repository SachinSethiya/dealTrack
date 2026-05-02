from django.urls import path
from . import views

urlpatterns = [
    path("", views.superadmin_login, name="superAdminLogin"),
    path("dashboard/", views.superAdminDashboard, name="superAdminDashboard"),
    path("toggle-showroom-status/<int:showroom_id>/", views.toggle_showroom_status, name="toggle_showroom_status"),
    path("delete-showroom/<int:showroom_id>/", views.delete_showroom, name="delete_showroom"),
    path("showroom/<int:showroom_id>/", views.showroom_detail, name="showroom_detail"),
    
    # User Management
    path("delete-user/", views.delete_user, name="delete_user"),
    
    # Showroom Management
    path("add-showroom/", views.add_showroom, name="add_showroom"),
    path("manage-showroom/", views.manage_showroom, name="manage_showroom"),
    path("edit-showroom/<int:showroom_id>/", views.edit_showroom, name="edit_showroom"),
    
    # Settings
    path("settings/", views.settings_page, name="settings_page"),
]