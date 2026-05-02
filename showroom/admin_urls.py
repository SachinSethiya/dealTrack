"""
Superadmin URL Configuration for DealTrack Application

This module contains URL patterns for the Superadmin dashboard functionality.
"""

from django.urls import path
from . import admin_views

app_name = 'superadmin'

urlpatterns = [
    # Superadmin Dashboard
    path('dashboard/', admin_views.superadmin_dashboard, name='superadmin_dashboard'),
    
    # User Management
    path('user/<int:user_id>/', admin_views.superadmin_user_detail, name='superadmin_user_detail'),
    path('user/<int:user_id>/toggle-status/', admin_views.superadmin_toggle_user_status, name='superadmin_toggle_user_status'),
    path('user/<int:user_id>/delete/', admin_views.superadmin_delete_user, name='superadmin_delete_user'),
    
    # Showroom Management (alias for user management)
    path('toggle-showroom-status/<int:showroom_id>/', admin_views.superadmin_toggle_user_status, name='toggle_showroom_status'),
]
