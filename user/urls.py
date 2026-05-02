from django.urls import path
from . import views

urlpatterns = [
    # List View (legacy)
    path('', views.user, name='user'),
    
    # CRUD Operations
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('create/', views.create_user, name='create_user'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('<int:user_id>/edit/', views.update_user, name='update_user'),
    path('<int:user_id>/delete/', views.delete_user, name='delete_user'),
]