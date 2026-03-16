from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def deal(request):
    return render(request,"deal/deals.html")