from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Customer
from showroom.models import Showroom
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Customer

@login_required
def add_customer(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        showroom=request.user
        Customer.objects.create(
            showroom_id=showroom,
            first_name=first_name,
            name=f"{first_name} {last_name}",
            last_name=last_name,
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            id_proof_number=request.POST.get('id_proof_number'),
            image=request.FILES.get('image')
        )
        return redirect("customer")

    return render(request, "customer/add_customer.html")

@login_required
def customer_list(request):
    customers = Customer.objects.filter(showroom_id=request.user)
    return render(request, "customer/customer.html", {"customers": customers})