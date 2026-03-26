from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from vehicle.models import Vehicle
from customer.models import Customer
from deal.models import Deal
from django.db.models import Sum

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")

User = get_user_model()

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        showroom_name = request.POST.get('showroom_name')
        phone = request.POST.get('phone')
        business_type = request.POST.get('business_type')
        gst_number = request.POST.get('gst_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        image = request.FILES.get('image')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")


        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            showroom_name=showroom_name,
            owner_name=f"{first_name} {last_name}",
            phone=phone,
            business_type=business_type,
            gst_number=gst_number,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            image=image
        )
        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")
    return render(request, "signup.html")


@login_required
def dashboard(request):
    showroom = request.user
    total_vehicle = Vehicle.objects.filter(showroom_id=showroom).count()
    sold_vehicle = Vehicle.objects.filter(showroom_id=showroom,vehicle_status = "sold").count()
    total_customer = Customer.objects.filter(showroom_id= showroom).count()
    profit = Deal.objects.filter(showroom_id=showroom).aggregate(total=Sum('profit'))['total'] or 0
        # ✅ Recent deals (latest 5)
    recent_deals = Deal.objects.filter(
    showroom_id=showroom
    ).select_related('vehicle_id', 'customer_id').order_by('-deal_date')[:5]
    recent_vehicles = Vehicle.objects.filter(showroom_id=showroom).order_by('-purchase_date')[:5]
    return render(request, "dashboard.html", {
        "total_vehicle": total_vehicle,
        "sold_vehicle":sold_vehicle,
        "total_customer":total_customer,
        "profit":profit,
        "recent_deals":recent_deals,
        "recent_vehicles":recent_vehicles
    })

def logout_view(request):
    logout(request)
    return redirect("login")


def settings(request):
    return render(request,"settings.html")