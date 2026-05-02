from django.urls import path
from . import views

urlpatterns = [
    # List View
    path('', views.ExpenseListView.as_view(), name='expense'),
    
    # CRUD Operations
    path('create/', views.ExpenseCreateView.as_view(), name='create_expense'),
    path('add/', views.add_expense, name='add_expense'),  # Keep for backward compatibility
    path('<str:expense_id>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('<str:expense_id>/edit/', views.ExpenseUpdateView.as_view(), name='update_expense'),
    path('<str:expense_id>/delete/', views.ExpenseDeleteView.as_view(), name='delete_expense'),
]