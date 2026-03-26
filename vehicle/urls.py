from django.urls import path

from . import views

urlpatterns = [
    path('', views.vehicle_list, name='vehicle'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('vehicle/<str:vehicle_id>', views.vehicle_detail,name="vehicle_detail"),
    # path("dashboard/", views.dashBoard_inventory, name="dashboard")
]
