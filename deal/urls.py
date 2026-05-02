from django.urls import path
from . import views

urlpatterns = [
    path('', views.DealListView.as_view(), name='deal'),
    path('new-deal/', views.DealCreateView.as_view(), name='new_deal'),
    path('add_deal/<str:vehicle_id>/', views.DealCreateView.as_view(), name='add_deal_with_vehicle'),
    path('add_deal/', views.DealCreateView.as_view(), name='add_deal'),
    path('deal-details/<str:deal_id>', views.DealDetailView.as_view(), name='deal_details'),
    path('send-follow-up/<str:deal_id>/', views.send_follow_up, name='send_follow_up'),
]