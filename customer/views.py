from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Customer
from showroom.models import Showroom
# Create your views here.

@login_required
def add_customer(request):

    if request.method == "POST":
        Customer.objects.create(
            showroom_id=request.user.id,   # logged in showroom
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            id_proof_number=request.POST.get('id_proof_number')
        )
        return redirect("customer")
    return render(request, "customer/add_customer.html")

@login_required
def customer_list(request):
    customers = Customer.objects.filter(showroom_id=request.user)
    return render(request, "customer/customer.html", {"customers": customers})