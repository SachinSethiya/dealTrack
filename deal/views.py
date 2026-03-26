from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from deal.models import Deal
from vehicle.models import Vehicle
from customer.models import Customer
from .models import Deal
from django.contrib.auth.decorators import login_required
from decimal import Decimal


# Create your views here.
@login_required
def deal(request):
    showroom = request.user
    deals = Deal.objects.filter(showroom_id=showroom)
    total_deals = Deal.objects.filter(showroom_id=showroom).count()
    return render(request,"deal/deals.html",{
        "deals": deals,
        "total_deals":total_deals
    })

def new_deal(request):
    showroom = request.user
    vehicles = Vehicle.objects.filter(
        showroom_id=showroom,
        vehicle_status="Avail"
        )    
    customer = Customer.objects.filter(showroom_id=showroom)
    return render(request,"deal/create_deal.html",{
        "vehicle": vehicles,
        "customer": customer
    })
    

def deal_details(request,deal_id):
    deal = get_object_or_404(Deal,deal_id=deal_id)
    return render(request,"deal/deal_details.html",{
        "deal":deal
    })


# @login_required 
# def deals_page(request):
#     showroom = request.user
#     total_deals = Deal.objects.filter(showroom_id=showroom).count()
#     return render(request,"deal/deal.html",{
#         "total_deal":total_deals
#     })

@login_required
def add_deal(request):
    if request.method == "POST":
        showroom = request.user
        vehicle_id = request.POST.get("vehicle_id")
        customer_id = request.POST.get("customer_id")
        print(request.POST)
        # 🔒 Validation
        if not vehicle_id or not customer_id:
            return HttpResponse("Please select vehicle and customer")
        try:
            vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
            customer = Customer.objects.get(id=customer_id)
        except (Vehicle.DoesNotExist, Customer.DoesNotExist):
            return HttpResponse("Invalid vehicle or customer")
        selling_price = vehicle.selling_price
        discount = Decimal(request.POST.get("discount") or 0)
        commission = Decimal(request.POST.get("commission") or 0)
        expenses = Decimal(request.POST.get("total_expenses") or 0)
        final_price = selling_price - discount
        profit = final_price - (commission + expenses)
        deal = Deal.objects.create(
            showroom_id = showroom,
            vehicle_id = vehicle,
            customer_id = customer,
            selling_price = selling_price,
            discount = discount,
            final_price = final_price,
            commission = commission,
            total_expenses = expenses,
            profit = profit,
            deal_date = request.POST.get("deal_date"),
            payment_status = request.POST.get("payment_status")
        )
        deal.deal_status = "completed"
        deal.save()
        vehicle.vehicle_status = "sold"
        vehicle.save()
        return redirect("deal")
    showroom = request.user
    vehicles = Vehicle.objects.filter(
        showroom_id=showroom,
        vehicle_status="Avail"
    ) 
    customer = Customer.objects.filter(showroom_id=showroom)
    return render(request,"deal/create_deal.html",{
        "vehicles": vehicles,
        "customer": customer
    })
