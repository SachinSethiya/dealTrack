from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicle'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle')

]