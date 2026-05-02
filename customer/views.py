from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from .models import Customer
from .forms import CustomerForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

def search_customers(request):
    query = request.GET.get('q', '').strip()
    showroom = request.user
    
    if not query:
        customers = Customer.objects.filter(showroom=showroom).order_by('-created_at')[:15]
    else:
        customers = Customer.objects.filter(
            Q(showroom=showroom) &
            (Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query) | Q(customer_id__icontains=query))
        ).order_by('-created_at')[:20]

    data = []
    for c in customers:
        data.append({
            'customer_id': c.customer_id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'id_proof_number': c.id_proof_number,
            'image_url': c.image.url if c.image and c.image.name != 'customer/user-profile' else None
        })

    return JsonResponse({'results': data})

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "customer/customer.html"
    context_object_name = "customers"
    paginate_by = 15

    def get_queryset(self):
        queryset = Customer.objects.filter(showroom=self.request.user).order_by('-created_at')
        
        # Pre-calculate analytics for each customer
        for customer in queryset:
            customer_deals_count = customer.deal_set.count()
            completed_deals_count = customer.deal_set.filter(deal_status='COMPLETED').count()
            total_deal_value = customer.deal_set.aggregate(Sum('final_price'))['final_price__sum'] or 0
            
            customer.analytics = {
                'deals_count': customer_deals_count,
                'completed_deals': completed_deals_count,
                'total_value': total_deal_value,
                'stage': 'Closed' if completed_deals_count > 0 else 'Negotiating' if customer_deals_count > 0 else 'Contacted',
                'stage_class': 'bg-closed-light' if completed_deals_count > 0 else 'bg-negotiating-light' if customer_deals_count > 0 else 'bg-contacted-light text-primary'
            }
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all customers for calculations
        customers = self.get_queryset()
        
        # Calculate basic metrics
        total_customers = customers.count()
        
        # Calculate trend indicators (compare with previous period)
        today = timezone.now().date()
        current_period_start = today - timedelta(days=30)
        previous_period_start = current_period_start - timedelta(days=30)
        
        # Current period data
        current_customers = Customer.objects.filter(
            showroom=self.request.user,
            created_at__date__gte=current_period_start
        )
        
        # Previous period data
        previous_customers = Customer.objects.filter(
            showroom=self.request.user,
            created_at__date__gte=previous_period_start,
            created_at__date__lt=current_period_start
        )
        
        # Calculate trends
        def calculate_trend(current_value, previous_value):
            if previous_value == 0:
                return 100 if current_value > 0 else 0
            return ((current_value - previous_value) / previous_value) * 100
        
        # Trend calculations
        current_total = current_customers.count()
        previous_total = previous_customers.count()
        customers_trend = calculate_trend(current_total, previous_total)
        
        # Get deals data for analytics
        from deal.models import Deal
        
        # Active deals count
        active_deals = Deal.objects.filter(
            showroom_id=self.request.user,
            deal_status='OPEN'
        ).count()
        
        # Hot leads (customers with recent activity)
        hot_leads = customers.filter(
            created_at__date__gte=today - timedelta(days=7)
        ).count()
        
        # This month customers
        this_month_customers = current_customers.count()
        
        # Pre-calculate customer analytics for template
        customer_analytics = {}
        for customer in customers:
            customer_deals_count = customer.deal_set.count()
            completed_deals_count = customer.deal_set.filter(deal_status='COMPLETED').count()
            total_deal_value = customer.deal_set.aggregate(Sum('final_price'))['final_price__sum'] or 0
            
            customer_analytics[customer.customer_id] = {
                'deals_count': customer_deals_count,
                'completed_deals': completed_deals_count,
                'total_value': total_deal_value,
                'stage': 'Closed' if completed_deals_count > 0 else 'Negotiating' if customer_deals_count > 0 else 'Contacted',
                'stage_class': 'bg-closed-light' if completed_deals_count > 0 else 'bg-negotiating-light' if customer_deals_count > 0 else 'bg-contacted-light text-primary'
            }
        
        # Add context variables
        context["total_customers"] = total_customers
        context["active_deals"] = active_deals
        context["hot_leads"] = hot_leads
        context["this_month_customers"] = this_month_customers
        context["customers_trend"] = customers_trend
        context["trend_period"] = "last 30 days"
        context["customer_analytics"] = customer_analytics
        
        return context

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer/add_customer.html"
    success_url = reverse_lazy('customer')

    def form_valid(self, form):
        form.instance.showroom = self.request.user
        form.instance.name = f"{form.instance.first_name} {form.instance.last_name_name}"
        messages.success(self.request, "Customer added successfully!")
        return super().form_valid(form)

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer/add_customer.html"
    success_url = reverse_lazy('customer')
    pk_url_kwarg = 'customer_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Customer, customer_id=self.kwargs['customer_id'], showroom=self.request.user)

    def form_valid(self, form):
        form.instance.name = f"{form.instance.first_name} {form.instance.last_name_name}"
        messages.success(self.request, "Customer updated successfully!")
        return super().form_valid(form)

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = "customer/customer_confirm_delete.html"
    context_object_name = "customer_obj"
    success_url = reverse_lazy('customer')
    pk_url_kwarg = 'customer_id'
    
    def get_object(self, queryset=None):
        return get_object_or_404(Customer, customer_id=self.kwargs['customer_id'], showroom=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        customer_obj = self.get_object()
        customer_name = customer_obj.name
        messages.success(request, f'Customer {customer_name} deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "customer/customer_detail.html"
    context_object_name = "customer"
    pk_url_kwarg = 'customer_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Customer.objects.select_related('showroom'), 
                               customer_id=self.kwargs['customer_id'], showroom=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Get customer's deals
        from deal.models import Deal
        customer_deals = Deal.objects.filter(
            customer_id=customer,
            showroom_id=self.request.user
        ).select_related('vehicle_id').order_by('-created_at')
        
        # Calculate customer analytics
        total_deals = customer_deals.count()
        completed_deals = customer_deals.filter(deal_status='COMPLETED').count()
        total_value = customer_deals.aggregate(Sum('final_price'))['final_price__sum'] or 0
        avg_deal_value = customer_deals.aggregate(Avg('final_price'))['final_price__avg'] or 0
        
        # Calculate customer stage based on deals
        if completed_deals > 0:
            customer_stage = 'Closed'
            customer_stage_class = 'bg-closed-light'
        elif total_deals > 0:
            customer_stage = 'Negotiating'
            customer_stage_class = 'bg-negotiating-light'
        else:
            customer_stage = 'Contacted'
            customer_stage_class = 'bg-contacted-light text-primary'
        
        # Add context variables
        context['customer_deals'] = customer_deals
        context['total_deals'] = total_deals
        context['completed_deals'] = completed_deals
        context['total_value'] = total_value
        context['avg_deal_value'] = avg_deal_value
        context['customer_stage'] = customer_stage
        context['customer_stage_class'] = customer_stage_class
        
        return context