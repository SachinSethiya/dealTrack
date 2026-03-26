from django.urls import path
from . import views

urlpatterns = [
    path('', views.deal, name='deal'),
    path('new-deal',views.new_deal,name='new_deal'),
    path('add_deal',views.add_deal,name="add_deal"),
    path('deal-details/<str:deal_id>',views.deal_details,name='deal_details')
]