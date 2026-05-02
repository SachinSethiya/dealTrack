from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from showroom.models import Showroom
from .models import AdminSettings
from .forms import ShowroomCreationForm, AdminSettingsForm, AdminPasswordChangeForm

def superadmin_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("superAdminDashboard")

    return render(request, "super_admin/login.html")


@login_required
def superAdminDashboard(request):
    if not request.user.is_superuser:
        return redirect("login")
    
    from showroom.models import Showroom
    from deal.models import Deal
    from django.db.models import Sum

    showrooms = Showroom.objects.filter(is_superuser=False).order_by('-created_at')
    total_showrooms = showrooms.count()
    active_showrooms = showrooms.filter(is_active=True).count()
    total_revenue = Deal.objects.filter(deal_status='COMPLETED').aggregate(total=Sum('final_price'))['total'] or 0

    context = {
        "showrooms": showrooms,
        "total_showrooms": total_showrooms,
        "active_showrooms": active_showrooms,
        "total_revenue": total_revenue,
    }

    return render(request, "super_admin/dashboard.html", context)


@login_required
def toggle_showroom_status(request, showroom_id):
    """
    Toggle Showroom Active Status
    
    Enables or disables a showroom account by toggling the is_active field.
    Only accepts POST requests for security.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("superAdminDashboard")
    
    showroom = get_object_or_404(Showroom, id=showroom_id)
    
    # Prevent superuser from deactivating themselves
    if showroom.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("superAdminDashboard")
    
    # Toggle active status
    showroom.is_active = not showroom.is_active
    showroom.save()
    
    status = "activated" if showroom.is_active else "deactivated"
    name = showroom.showroom_name if showroom.showroom_name else getattr(showroom, "username", "Showroom")
    messages.success(request, f"Showroom {name} has been {status}.")
    
    return redirect("superAdminDashboard")


@login_required
def delete_showroom(request, showroom_id):
    """
    Delete Showroom
    
    Permanently deletes a showroom and all associated data.
    Only accepts POST requests for security.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("superAdminDashboard")
    
    showroom = get_object_or_404(Showroom, id=showroom_id)
    
    # Prevent superuser from deleting themselves
    if showroom.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect("superAdminDashboard")
    
    # Store showroom name for message
    showroom_name = showroom.showroom_name or showroom.username
    
    # Delete the showroom (this will cascade delete related data)
    showroom.delete()
    
    messages.success(request, f"Showroom {showroom_name} has been deleted successfully.")
    
    return redirect("superAdminDashboard")


@login_required
def showroom_detail(request, showroom_id):
    """
    Showroom Detail Page
    
    Displays detailed information about a specific showroom.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    showroom = get_object_or_404(Showroom, id=showroom_id)
    
    # Get related data if available
    try:
        from vehicle.models import Vehicle
        from customer.models import Customer
        from deal.models import Deal
        
        vehicle_count = Vehicle.objects.filter(showroom_id=showroom).count()
        customer_count = Customer.objects.filter(showroom=showroom).count()
        deal_count = Deal.objects.filter(showroom_id=showroom).count()
        
        # Recent activity
        recent_vehicles = Vehicle.objects.filter(
            showroom_id=showroom
        ).order_by('-purchase_date')[:5]
        
        recent_deals = Deal.objects.filter(
            showroom_id=showroom
        ).order_by('-deal_date')[:5]
        
    except ImportError:
        # Handle case where related models don't exist
        vehicle_count = 0
        customer_count = 0
        deal_count = 0
        recent_vehicles = []
        recent_deals = []
    
    context = {
        'showroom': showroom,
        'vehicle_count': vehicle_count,
        'customer_count': customer_count,
        'deal_count': deal_count,
        'recent_vehicles': recent_vehicles,
        'recent_deals': recent_deals,
    }
    
    return render(request, 'super_admin/showroom_detail.html', context)


@login_required
def delete_user(request):
    """
    Delete User Page
    
    Lists all users and provides deletion functionality.
    Only superadmin can access this page.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(Showroom, id=user_id)
            
            # Prevent superuser from deleting themselves
            if user.id == request.user.id:
                messages.error(request, "You cannot delete your own account.")
                return redirect("delete_user")
            
            # Prevent deleting other superusers
            if user.is_superuser:
                messages.error(request, "You cannot delete another superuser account.")
                return redirect("delete_user")
            
            # Store user name for message
            user_name = user.showroom_name or user.username
            
            # Delete the user
            user.delete()
            
            messages.success(request, f"User {user_name} has been deleted successfully.")
        else:
            messages.error(request, "Invalid user ID.")
        
        return redirect("delete_user")
    
    # Get all users except superusers
    users = Showroom.objects.filter(is_superuser=False).order_by('-created_at')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
    }
    
    return render(request, 'super_admin/delete_user.html', context)


@login_required
def add_showroom(request):
    """
    Add Showroom Page
    
    Provides a form to create new showroom accounts.
    Only superadmin can access this page.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    if request.method == "POST":
        form = ShowroomCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the showroom with proper password handling
                    showroom = form.save()
                    
                    messages.success(request, 
                        f"Showroom '{showroom.showroom_name}' has been created successfully. "
                        f"Username: {showroom.username}, Email: {showroom.email}"
                    )
                    
                    # Redirect to manage showroom page
                    return redirect("manage_showroom")
                    
            except Exception as e:
                messages.error(request, f"Error creating showroom: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShowroomCreationForm()
    
    context = {
        'form': form,
        'title': 'Add New Showroom'
    }
    
    return render(request, 'super_admin/add_showroom.html', context)


@login_required
def manage_showroom(request):
    """
    Manage Showroom Page
    
    Lists all showrooms with management options.
    Only superadmin can access this page.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    # Get all showrooms except superusers
    showrooms = Showroom.objects.filter(is_superuser=False).order_by('-created_at')
    
    context = {
        'showrooms': showrooms,
        'total_showrooms': showrooms.count(),
        'active_showrooms': showrooms.filter(is_active=True).count(),
        'inactive_showrooms': showrooms.filter(is_active=False).count(),
    }
    
    return render(request, 'super_admin/manage_showroom.html', context)


@login_required
def edit_showroom(request, showroom_id):
    """
    Edit Showroom Page
    
    Provides a form to edit existing showroom accounts.
    Only superadmin can access this page.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    showroom = get_object_or_404(Showroom, id=showroom_id)
    
    # Prevent editing superuser accounts
    if showroom.is_superuser:
        messages.error(request, "You cannot edit superuser accounts.")
        return redirect("manage_showroom")
    
    if request.method == "POST":
        # Create form with instance and POST data
        form = ShowroomCreationForm(request.POST, request.FILES, instance=showroom)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the updated showroom
                    updated_showroom = form.save()
                    
                    messages.success(request, 
                        f"Showroom '{updated_showroom.showroom_name}' has been updated successfully."
                    )
                    
                    return redirect("manage_showroom")
                    
            except Exception as e:
                messages.error(request, f"Error updating showroom: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Create form with existing instance
        form = ShowroomCreationForm(instance=showroom)
        # Pre-fill password fields as empty for security
        form.fields['password'].initial = ''
        form.fields['confirm_password'].initial = ''
    
    context = {
        'form': form,
        'showroom': showroom,
        'title': f'Edit Showroom - {showroom.showroom_name}'
    }
    
    return render(request, 'super_admin/add_showroom.html', context)


@login_required
def settings_page(request):
    """
    Settings Page
    
    Provides platform-wide settings and admin password change.
    Only superadmin can access this page.
    """
    if not request.user.is_superuser:
        return redirect("login")
    
    # Get or create admin settings with error handling
    try:
        admin_settings = AdminSettings.get_settings()
        db_available = True
    except Exception as e:
        # Handle database connection or table missing errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error accessing AdminSettings: {e}")
        
        # Create a fallback settings instance
        admin_settings = AdminSettings(
            allow_new_showroom_registration=True,
            maintenance_mode=False,
            platform_announcement="",
            max_showrooms_per_user=1,
            email_notifications_enabled=True
        )
        db_available = False
        messages.warning(request, "Database settings unavailable. Using default values. Please contact administrator.")
    
    if request.method == "POST":
        # Only allow settings changes if database is available
        if not db_available:
            messages.error(request, "Settings cannot be saved due to database issues. Please contact administrator.")
            settings_form = AdminSettingsForm(instance=admin_settings)
            password_form = AdminPasswordChangeForm()
        else:
            # Determine which form was submitted
            if 'platform_settings' in request.POST:
                # Platform settings form
                settings_form = AdminSettingsForm(request.POST, instance=admin_settings)
                password_form = AdminPasswordChangeForm()
                
                if settings_form.is_valid():
                    try:
                        settings_form.save()
                        messages.success(request, "Platform settings have been updated successfully.")
                        return redirect("settings_page")
                    except Exception as e:
                        logger.error(f"Error saving settings: {e}")
                        messages.error(request, "Error saving settings. Please try again.")
                else:
                    messages.error(request, "Please correct the errors in platform settings.")
            
            elif 'password_change' in request.POST:
                # Password change form
                password_form = AdminPasswordChangeForm(request.POST)
                settings_form = AdminSettingsForm(instance=admin_settings)
                
                if password_form.is_valid():
                    # Validate current password
                    current_password = password_form.cleaned_data.get('current_password')
                    if not request.user.check_password(current_password):
                        messages.error(request, "Current password is incorrect.")
                    else:
                        # Change password
                        new_password = password_form.cleaned_data.get('new_password')
                        request.user.set_password(new_password)
                        request.user.save()
                        
                        # Update session to prevent logout
                        update_session_auth_hash(request, request.user)
                        
                        messages.success(request, "Your password has been changed successfully.")
                        return redirect("settings_page")
                else:
                    messages.error(request, "Please correct the errors in password form.")
            
            else:
                # Unknown form submission
                messages.error(request, "Invalid form submission.")
                settings_form = AdminSettingsForm(instance=admin_settings)
                password_form = AdminPasswordChangeForm()
    else:
        settings_form = AdminSettingsForm(instance=admin_settings)
        password_form = AdminPasswordChangeForm()
    
    context = {
        'settings_form': settings_form,
        'password_form': password_form,
        'admin_settings': admin_settings,
        'db_available': db_available,
    }
    
    return render(request, 'super_admin/settings.html', context)