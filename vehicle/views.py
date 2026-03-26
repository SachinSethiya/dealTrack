from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vehicle, VehicleImage
from showroom.models import Showroom
from django.http import HttpResponse
from decimal import Decimal

@login_required
def add_vehicle(request):
    if request.method == "POST":
        # Create and capture the Vehicle instance
        showroom = request.user

        vehicle = Vehicle.objects.create(
            showroom_id=showroom,

            company=(request.POST.get("company") or "").upper(),
            model_name=(request.POST.get("model_name") or "").strip(),
            variant=(request.POST.get("variant") or "").upper(),
            color=(request.POST.get("color") or "").title(),

            manufacturing_year=request.POST.get("manufacturing_year") or None,
            km_driven=request.POST.get("km_driven") or 0,
            mileage=request.POST.get("mileage") or "",

            purchase_price=Decimal(request.POST.get("purchase_price") or 0),
            selling_price=Decimal(request.POST.get("selling_price") or 0),

            purchase_date=request.POST.get("purchase_date") or None,

            fuel_type=request.POST.get("fuel_type"),
            transmission=request.POST.get("transmission"),

            registration_no=(request.POST.get("registration_number") or "").upper(),
            chasis_no=(request.POST.get("chassis_number") or "").upper(),
        )
        
        # Handle the image uploads
        image_files = request.FILES.getlist("images")
        if image_files:
            for index, image_file in enumerate(image_files[:4]):
                VehicleImage.objects.create(
                    vehicle=vehicle,
                    image=image_file,
                    is_primary=(index == 0)
                )
            
        return redirect("vehicle")
    return render(request, "vehicle/add_vehicle.html")

@login_required
def vehicle_list(request):
    showroom = request.user
    vehicles = Vehicle.objects.filter(showroom_id=showroom)
    vehicle_data = []
    for vehicle in vehicles:
        primary_image = vehicle.images.filter(is_primary=True).first()
        vehicle_data.append({
            "vehicle": vehicle,
            "primary_image": primary_image
        })

    return render(request, "vehicle/vehicle_list.html", {
        "vehicle_data": vehicle_data
    })

@login_required
def vehicle_detail(request, vehicle_id):
    vehicles = get_object_or_404(Vehicle, vehicle_id=vehicle_id)
    
    if request.method == "POST":
        image_files = request.FILES.getlist("new_images")
        if image_files:
            current_count = vehicles.images.count()
            for image_file in image_files:
                if current_count < 4:
                    VehicleImage.objects.create(
                        vehicle=vehicles,
                        image=image_file,
                        is_primary=(current_count == 0)
                    )
                    current_count += 1
        return redirect("vehicle_detail", vehicle_id=vehicle_id)

    images = vehicles.images.all()
    primary_image = vehicles.images.filter(is_primary=True).first()

    return render(request, "vehicle/vehicle_detail.html", {
        "vehicles": vehicles,
        "images": images,
        "primary_image": primary_image
    })


