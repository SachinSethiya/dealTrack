"""
Superadmin Views for DealTrack Application

This module contains views for the Superadmin dashboard functionality:
- List all users/showrooms
- View detailed showroom information for a specific user
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import Http404

# Get the custom user model
User = get_user_model()


def is_superadmin(user):
    """
    Check if the current user is a superadmin.
    You can modify this logic based on your superadmin identification method.
    """
    # Option 1: Check for superuser status
    if user.is_superuser:
        return True
    
    # Option 2: Check for specific superadmin role/permission
    # if user.has_perm('showroom.superadmin_access'):
    #     return True
    
    # Option 3: Check for specific username pattern
    # if user.username.startswith('admin_'):
    #     return True
    
    return False


@login_required(login_url='login')
@user_passes_test(is_superadmin, login_url='login')
def superadmin_dashboard(request):
    """
    Superadmin Dashboard View
    
    Displays all users/showrooms in a paginated list.
    Supports search functionality for filtering users.
    """
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Fetch all users with optional search filtering
    users_queryset = User.objects.all().order_by('-created_at')
    
    if search_query:
        users_queryset = users_queryset.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(showroom_name__icontains=search_query) |
            Q(owner_name__icontains=search_query)
        )
    
    # Pagination - 10 users per page
    paginator = Paginator(users_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics for dashboard
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_users = User.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_users': total_users,
        'active_users': active_users,
        'recent_users': recent_users,
        'title': 'Superadmin Dashboard - Users'
    }
    
    return render(request, 'superadmin/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(is_superadmin, login_url='login')
def superadmin_user_detail(request, user_id):
    """
    User Detail View
    
    Displays detailed information about a specific user/showroom.
    Shows all showroom-related fields and associated data.
    """
    # Get the user or return 404
    user = get_object_or_404(User, id=user_id)
    
    # Get additional related data if needed
    # For example: vehicles, customers, deals associated with this showroom
    try:
        from vehicle.models import Vehicle
        from customer.models import Customer
        from deal.models import Deal
        
        vehicle_count = Vehicle.objects.filter(showroom_id=user).count()
        customer_count = Customer.objects.filter(showroom=user).count()
        deal_count = Deal.objects.filter(showroom_id=user).count()
        
        # Recent activity
        recent_vehicles = Vehicle.objects.filter(
            showroom_id=user
        ).order_by('-purchase_date')[:5]
        
        recent_deals = Deal.objects.filter(
            showroom_id=user
        ).order_by('-deal_date')[:5]
        
    except ImportError:
        # Handle case where related models don't exist
        vehicle_count = 0
        customer_count = 0
        deal_count = 0
        recent_vehicles = []
        recent_deals = []
    
    context = {
        'user': user,
        'vehicle_count': vehicle_count,
        'customer_count': customer_count,
        'deal_count': deal_count,
        'recent_vehicles': recent_vehicles,
        'recent_deals': recent_deals,
        'title': f'User Details - {user.showroom_name or user.username}'
    }
    
    return render(request, 'superadmin/user_detail.html', context)


@login_required(login_url='login')
@user_passes_test(is_superadmin, login_url='login')
def superadmin_toggle_user_status(request, user_id):
    """
    Toggle User Active Status
    
    Enables or disables a user account.
    """
    user = get_object_or_404(User, id=user_id)
    
    if user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('superadmin_user_detail', user_id=user_id)
    
    # Toggle active status
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    
    return redirect('superadmin_user_detail', user_id=user_id)


@login_required(login_url='login')
@user_passes_test(is_superadmin, login_url='login')
def toggle_showroom_status(request, showroom_id):
    """
    Toggle Showroom Active Status
    
    Enables or disables a showroom account.
    This is an alias for superadmin_toggle_user_status but accepts showroom_id parameter.
    """
    showroom = get_object_or_404(User, id=showroom_id)
    
    if showroom.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('superadmin_user_detail', user_id=showroom_id)
    
    # Toggle active status
    showroom.is_active = not showroom.is_active
    showroom.save()
    
    status = "activated" if showroom.is_active else "deactivated"
    messages.success(request, f"Showroom {showroom.showroom_name|default:showroom.username} has been {status}.")
    
    return redirect('superadmin_user_detail', user_id=showroom_id)


@login_required(login_url='login')
@user_passes_test(is_superadmin, login_url='login')
def superadmin_delete_user(request, user_id):
    """
    Delete User
    
    Permanently deletes a user and all associated data.
    Use with caution - consider soft delete instead.
    """
    user = get_object_or_404(User, id=user_id)
    
    if user.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('superadmin_user_detail', user_id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User {username} has been deleted successfully.")
        return redirect('superadmin_dashboard')
    
    return redirect('superadmin_user_detail', user_id=user_id)


# Import timezone for recent users calculation
from django.utils import timezone
from datetime import timedelta
