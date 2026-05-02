from django.urls import path

from . import views

urlpatterns = [
    path('', views.VehicleListView.as_view(), name='vehicle'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('vehicle/<str:vehicle_id>', views.vehicle_detail,name="vehicle_detail"),
    path('vehicle/edit/<str:vehicle_id>/', views.edit_vehicle, name="edit_vehicle"),
    path('vehicle/<str:vehicle_id>/action/', views.vehicle_action, name="vehicle_action"),
    path('vehicle/<str:vehicle_id>/mark-unsold/', views.mark_as_unsold, name="mark_as_unsold"),
]
