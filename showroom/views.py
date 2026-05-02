from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
from vehicle.models import Vehicle
from customer.models import Customer
from deal.models import Deal
from django.db.models import Sum
from django.views.decorators.cache import cache_control
from .forms import ShowroomSettingsForm

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


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
    request.session.flush()
    return redirect("login")


@login_required(login_url='login')
def profile_view(request):
    """
    View-only profile page that displays user/showroom information.
    This is the main profile viewing page.
    """
    # Just render the template with user data
    return render(request, 'settings.html')


@login_required(login_url='login')
def edit_profile_view(request):
    """
    Edit profile page with form for updating user/showroom information.
    Handles both GET (display form) and POST (save changes) requests.
    Only updates fields that have actual values (partial updates).
    """
    showroom = request.user
    
    if request.method == 'POST':
        form = ShowroomSettingsForm(request.POST, request.FILES, instance=showroom)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Get cleaned data
                    cleaned_data = form.cleaned_data
                    
                    # Only update fields that have values (partial update logic)
                    updated_fields = []
                    
                    # Update username only if provided
                    username = cleaned_data.get('username')
                    if username and username.strip():
                        showroom.username = username.strip()
                        updated_fields.append('username')
                    
                    # Update email only if provided
                    email = cleaned_data.get('email')
                    if email and email.strip():
                        showroom.email = email.strip()
                        updated_fields.append('email')
                    
                    # Update showroom_name only if provided
                    showroom_name = cleaned_data.get('showroom_name')
                    if showroom_name and showroom_name.strip():
                        showroom.showroom_name = showroom_name.strip()
                        updated_fields.append('showroom_name')
                    
                    # Update owner_name only if provided
                    owner_name = cleaned_data.get('owner_name')
                    if owner_name and owner_name.strip():
                        showroom.owner_name = owner_name.strip()
                        updated_fields.append('owner_name')
                    
                    # Update phone_number only if provided
                    phone_number = cleaned_data.get('phone_number')
                    if phone_number and phone_number.strip():
                        showroom.phone_number = phone_number.strip()
                        updated_fields.append('phone_number')
                    
                    # Update address only if provided
                    address = cleaned_data.get('address')
                    if address and address.strip():
                        showroom.address = address.strip()
                        updated_fields.append('address')
                    
                    # Update city only if provided
                    city = cleaned_data.get('city')
                    if city and city.strip():
                        showroom.city = city.strip()
                        updated_fields.append('city')
                    
                    # Update state only if provided
                    state = cleaned_data.get('state')
                    if state and state.strip():
                        showroom.state = state.strip()
                        updated_fields.append('state')
                    
                    # Update pincode only if provided
                    pincode = cleaned_data.get('pincode')
                    if pincode and pincode.strip():
                        showroom.pincode = pincode.strip()
                        updated_fields.append('pincode')
                    
                    # Update gst_number only if provided
                    gst_number = cleaned_data.get('gst_number')
                    if gst_number and gst_number.strip():
                        showroom.gst_number = gst_number.strip()
                        updated_fields.append('gst_number')
                    
                    # Update business_type only if provided
                    business_type = cleaned_data.get('business_type')
                    if business_type and business_type.strip():
                        showroom.business_type = business_type.strip()
                        updated_fields.append('business_type')
                    
                    # Update primary_color only if provided
                    primary_color = cleaned_data.get('primary_color')
                    if primary_color and primary_color.strip():
                        showroom.primary_color = primary_color.strip()
                        updated_fields.append('primary_color')
                    
                    # Update image only if new file is uploaded
                    image = cleaned_data.get('image')
                    if image:
                        showroom.image = image
                        updated_fields.append('image')
                    
                    # Save the showroom object
                    if updated_fields:
                        showroom.save()
                        
                        # Create success message with details
                        if len(updated_fields) == 1:
                            messages.success(request, f'{updated_fields[0].replace("_", " ").title()} has been updated successfully!')
                        else:
                            messages.success(request, f'Your profile has been updated successfully! ({len(updated_fields)} fields changed)')
                    else:
                        messages.info(request, 'No changes were made. Please fill at least one field to update.')
                    
                    # Redirect back to profile view page
                    return redirect('profile')
                    
            except Exception as e:
                messages.error(request, f'An error occurred while saving your profile: {str(e)}')
        else:
            # Form validation failed
            messages.error(request, 'Please correct the errors below.')
    
    else:
        # GET request - initialize form with current user data
        form = ShowroomSettingsForm(instance=showroom)
    
    # Add additional context for template
    context = {
        'form': form,
        'showroom': showroom,
    }
    
    return render(request, 'edit_profile.html', context)


@login_required(login_url='login')
def settings(request):
    """
    Legacy settings view - redirect to profile view
    """
    return redirect('profile')


from django.db.models import Q

@login_required(login_url='login')
def global_search(request):
    query = request.GET.get('q', '').strip()
    showroom = request.user
    vehicles = []
    customers = []
    if query:
        vehicles = Vehicle.objects.filter(
            Q(showroom_id=showroom) &
            (Q(model_name__icontains=query) | Q(company__icontains=query) | Q(vehicle_id__icontains=query))
        )
        customers = Customer.objects.filter(
            Q(showroom=showroom) &
            (Q(name__icontains=query) | Q(phone__icontains=query) | Q(customer_id__icontains=query))
        )
    return render(request, "search_results.html", {
        "query": query,
        "vehicles": vehicles,
        "customers": customers
    })


@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Simple endpoint to provide CSRF token for debugging purposes.
    This helps resolve CSRF token issues in development.
    """
    return HttpResponse("CSRF token refreshed", content_type="text/plain")