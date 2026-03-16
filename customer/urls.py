from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer'),
    path('add-customer', views.add_customer,name='add_customer')
]