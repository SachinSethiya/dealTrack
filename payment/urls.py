from django.urls import path
from . import views

urlpatterns = [
    # List View (legacy)
    path('', views.payment, name='payment'),
    
    # CRUD Operations
    path('list/', views.PaymentListView.as_view(), name='payment_list'),
    path('create/', views.create_payment, name='create_payment'),
    path('<str:payment_id>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('<str:payment_id>/edit/', views.update_payment, name='update_payment'),
    path('<str:payment_id>/delete/', views.delete_payment, name='delete_payment'),
]