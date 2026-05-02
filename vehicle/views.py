from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, VehicleImage
from showroom.models import Showroom
from django.http import HttpResponse
from decimal import Decimal
from .forms import VehicleForm, VehicleUpdateForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch

@login_required
def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.showroom_id = request.user
            vehicle.save()
            
            # Handle the image uploads
            image_files = request.FILES.getlist("images")
            if image_files:
                for index, image_file in enumerate(image_files[:4]):
                    VehicleImage.objects.create(
                        vehicle=vehicle,
                        image=image_file,
                        is_primary=(index == 0)
                    )
            messages.success(request, "Vehicle added successfully.")
            return redirect("vehicle")
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = VehicleForm()
        
    return render(request, "vehicle/add_vehicle.html", {"form": form})
class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = "vehicle/vehicle_list.html"
    context_object_name = "vehicle_data"
    paginate_by = 12

    def get_queryset(self):
        # Prefetch images specifically filtering by is_primary=True to obliterate N+1
        primary_image_prefetch = Prefetch(
            'images',
            queryset=VehicleImage.objects.filter(is_primary=True),
            to_attr='primary_images'
        )
        return Vehicle.objects.prefetch_related(primary_image_prefetch).filter(
            showroom_id=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Reform the exact expected context block so we don't break their template
        vehicle_data = []
        for vehicle in context['vehicle_data']:
            primary_img = vehicle.primary_images[0] if vehicle.primary_images else None
            vehicle_data.append({
                "vehicle": vehicle,
                "primary_image": primary_img
            })
        context['vehicle_data'] = vehicle_data
        return context


@login_required
def edit_vehicle(request, vehicle_id):
    """
    Vehicle Update View - Handles editing existing vehicles
    Uses VehicleUpdateForm for better validation and user experience
    """
    vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id, showroom_id=request.user)
    
    if request.method == "POST":
        form = VehicleUpdateForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            # Save the updated vehicle
            updated_vehicle = form.save()
            
            # Handle image uploads if any
            image_files = request.FILES.getlist("images")
            if image_files:
                current_count = updated_vehicle.images.count()
                for index, image_file in enumerate(image_files[:4]):
                    VehicleImage.objects.create(
                        vehicle=updated_vehicle,
                        image=image_file,
                        is_primary=(current_count == 0 and index == 0)
                    )
            
            messages.success(request, "Vehicle updated successfully.")
            return redirect("vehicle_detail", vehicle_id=vehicle.vehicle_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill form with existing vehicle data
        form = VehicleUpdateForm(instance=vehicle)
        
    return render(request, "vehicle/edit_vehicle.html", {
        "form": form,
        "vehicle": vehicle
    })

@login_required
def vehicle_detail(request, vehicle_id):
    vehicles = get_object_or_404(Vehicle, vehicle_id=vehicle_id, showroom_id=request.user)
    
    if request.method == "POST":
        images = request.FILES.getlist('images')
        if images:
            current_count = vehicles.images.count()
            for image in images:
                if current_count < 4:
                    VehicleImage.objects.create(
                        vehicle=vehicles,
                        image=image,
                        is_primary=(current_count == 0)
                    )
                    current_count += 1
        return redirect("vehicle_detail", vehicle_id=vehicle_id)

    images = vehicles.images.all()
    primary_image = vehicles.images.filter(is_primary=True).first()
    
    # 🔹 Fetch related deal if vehicle is sold
    related_deal = None
    if vehicles.is_sold:
        from deal.models import Deal
        try:
            related_deal = Deal.objects.get(vehicle_id=vehicles)
        except Deal.DoesNotExist:
            pass

    return render(request, "vehicle/vehicle_detail.html", {
        "vehicles": vehicles,
        "images": images,
        "primary_image": primary_image,
        "related_deal": related_deal
    })

@login_required
def vehicle_action(request, vehicle_id):
    """
    Handle vehicle status actions including mark as sold, mark as unsold, etc.
    """
    if request.method == "POST":
        vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id, showroom_id=request.user)
        action = request.POST.get("action")
        
        if action == "mark_sold":
            vehicle.vehicle_status = "sold"
            vehicle.save()
            messages.success(request, f"{vehicle} marked as sold.")
        elif action == "mark_unsold":
            # Mark as unsold - set status to available
            vehicle.vehicle_status = "Avail"
            vehicle.save()
            messages.success(request, f"{vehicle} marked as available (unsold).")
        elif action == "archive":
            vehicle.vehicle_status = "maintanance"
            vehicle.save()
            messages.success(request, f"{vehicle} moved to maintenance.")
        elif action == "reserve":
            vehicle.vehicle_status = "reser"
            vehicle.save()
            messages.success(request, f"{vehicle} marked as reserved.")
            
    return redirect("vehicle_detail", vehicle_id=vehicle_id)


@login_required
def mark_as_unsold(request, vehicle_id):
    """
    Dedicated view to mark a vehicle as unsold (available)
    This provides a clean URL for the "Mark as Unsold" action
    """
    vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id, showroom_id=request.user)
    
    if request.method == "POST":
        # Only allow marking as unsold if currently sold
        if vehicle.vehicle_status == "sold":
            vehicle.vehicle_status = "Avail"
            vehicle.save()
            messages.success(request, f"{vehicle} has been marked as available (unsold).")
        else:
            messages.info(request, f"{vehicle} is already available.")
    
    return redirect("vehicle_detail", vehicle_id=vehicle_id)

@login_required
def delete_vehicle(request, vehicle_id):
    if request.method == "POST":
        vehicle = get_object_or_404(Vehicle, vehicle_id=vehicle_id, showroom_id=request.user)
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
        return redirect("vehicle")
    return redirect("vehicle_detail", vehicle_id=vehicle_id)
