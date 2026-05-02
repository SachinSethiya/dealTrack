from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name="profile"),
    path('profile/edit/', views.edit_profile_view, name="edit_profile"),
    path('settings/',views.settings,name="setting"),
    path('search/', views.global_search, name="global_search"),
    path('get-csrf-token/', views.get_csrf_token, name="get_csrf_token"),
    
    # Superadmin URLs
    path('superadmin/', include('showroom.admin_urls')),
]