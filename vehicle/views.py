from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from showroom.models import Showroom


@login_required
def add_vehicle(request):
    if request.method == "POST":
        Vehicle.objects.create(
            showroom_id=request.user,   # logged in showroom
            company=request.POST.get("company"),
            model_name=request.POST.get("model_name"),
            variant=request.POST.get("variant"),
            manufacturing_year=request.POST.get("manufacturing_year"),
            fuel_type=request.POST.get("fuel_type"),
            transmission=request.POST.get("transmission"),
            color=request.POST.get("color"),
            purchase_price=request.POST.get("purchase_price"),
            km_driven=request.POST.get("km_driven"),
            purchase_date=request.POST.get("purchase_date"),
            registration_no=request.POST.get("registration_no"),
            chasis_no=request.POST.get("chasis_no")
        )
        return redirect("vehicle")
    return render(request, "vehicle/add_vehicle.html")

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(showroom_id=request.user)
    return render(request, "vehicle/vehicle.html", {"vehicles": vehicles})