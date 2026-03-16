from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def expense(request):
    return render(request,"expense/expense.html")