from django.urls import path
from . import views

urlpatterns = [
    # API
    path('api/search-customers/', views.search_customers, name='search_customers'),
    
    # CRUD Operations
    path('', views.CustomerListView.as_view(), name='customer'),
    path('add-customer', views.CustomerCreateView.as_view(), name='add_customer'),
    path('edit-customer/<str:customer_id>', views.CustomerUpdateView.as_view(), name='edit_customer'),
    path('delete-customer/<str:customer_id>', views.CustomerDeleteView.as_view(), name='delete_customer'),
    path('customer-detail/<str:customer_id>/', views.CustomerDetailView.as_view(), name='customer_detail'),
]