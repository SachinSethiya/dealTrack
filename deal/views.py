from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from deal.models import Deal
from vehicle.models import Vehicle
from customer.models import Customer
from decimal import Decimal

class DealListView(LoginRequiredMixin, ListView):
    model = Deal
    template_name = "deal/deals.html"
    context_object_name = "deals"
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Deal.objects.select_related('vehicle_id', 'customer_id').filter(showroom_id=self.request.user)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(vehicle_id__model_name__icontains=search_query) |
                Q(vehicle_id__company__icontains=search_query) |
                Q(customer_id__name__icontains=search_query) |
                Q(deal_id__icontains=search_query)
            )
        
        # Payment status filter
        payment_status = self.request.GET.get('payment_status', '')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Deal status filter
        deal_status = self.request.GET.get('deal_status', '')
        if deal_status:
            queryset = queryset.filter(deal_status=deal_status)
        
        # Date filter
        date_filter = self.request.GET.get('date_filter', '')
        if date_filter:
            today = timezone.now().date()
            if date_filter == 'this_month':
                queryset = queryset.filter(deal_date__month=today.month, deal_date__year=today.year)
            elif date_filter == 'last_quarter':
                # Last quarter logic
                if today.month <= 3:
                    queryset = queryset.filter(deal_date__month__gte=10, deal_date__year=today.year-1)
                elif today.month <= 6:
                    queryset = queryset.filter(deal_date__month__gte=1, deal_date__month__lte=3, deal_date__year=today.year)
                elif today.month <= 9:
                    queryset = queryset.filter(deal_date__month__gte=4, deal_date__month__lte=6, deal_date__year=today.year)
                else:
                    queryset = queryset.filter(deal_date__month__gte=7, deal_date__month__lte=9, deal_date__year=today.year)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all deals for calculations
        deals = self.get_queryset()
        
        # Calculate aggregations
        total_deals = deals.count()
        pipeline_value = deals.aggregate(Sum("final_price"))["final_price__sum"] or 0
        avg_deal_size = deals.aggregate(Avg("final_price"))["final_price__avg"] or 0
        closed_deals = deals.filter(deal_status="COMPLETED").count()
        
        # Calculate close rate
        close_rate = (closed_deals / total_deals) * 100 if total_deals > 0 else 0
        
        # Calculate trend indicators (compare with previous period)
        today = timezone.now().date()
        current_period_start = today - timedelta(days=30)
        previous_period_start = current_period_start - timedelta(days=30)
        
        # Current period data
        current_deals = Deal.objects.filter(
            showroom_id=self.request.user,
            created_at__date__gte=current_period_start
        )
        
        # Previous period data
        previous_deals = Deal.objects.filter(
            showroom_id=self.request.user,
            created_at__date__gte=previous_period_start,
            created_at__date__lt=current_period_start
        )
        
        # Calculate trends
        def calculate_trend(current_value, previous_value):
            if previous_value == 0:
                return 100 if current_value > 0 else 0
            return ((current_value - previous_value) / previous_value) * 100
        
        # Trend calculations
        current_total = current_deals.count()
        previous_total = previous_deals.count()
        total_deals_trend = calculate_trend(current_total, previous_total)
        
        current_pipeline = current_deals.aggregate(Sum("final_price"))["final_price__sum"] or 0
        previous_pipeline = previous_deals.aggregate(Sum("final_price"))["final_price__sum"] or 0
        pipeline_trend = calculate_trend(current_pipeline, previous_pipeline)
        
        current_closed = current_deals.filter(deal_status="COMPLETED").count()
        previous_closed = previous_deals.filter(deal_status="COMPLETED").count()
        current_close_rate = (current_closed / current_total * 100) if current_total > 0 else 0
        previous_close_rate = (previous_closed / previous_total * 100) if previous_total > 0 else 0
        close_rate_trend = calculate_trend(current_close_rate, previous_close_rate)
        
        current_avg = current_deals.aggregate(Avg("final_price"))["final_price__avg"] or 0
        previous_avg = previous_deals.aggregate(Avg("final_price"))["final_price__avg"] or 0
        avg_deal_trend = calculate_trend(current_avg, previous_avg)
        
        # Add context variables
        context["total_deals"] = total_deals
        context["pipeline_value"] = pipeline_value
        context["avg_deal_size"] = avg_deal_size
        context["close_rate"] = close_rate
        
        # Add trend indicators
        context["total_deals_trend"] = total_deals_trend
        context["pipeline_trend"] = pipeline_trend
        context["close_rate_trend"] = close_rate_trend
        context["avg_deal_trend"] = avg_deal_trend
        
        # Add period information
        context["trend_period"] = "last 30 days"
        
        # Add filter context
        context["current_search"] = self.request.GET.get('search', '')
        context["current_payment_status"] = self.request.GET.get('payment_status', '')
        context["current_deal_status"] = self.request.GET.get('deal_status', '')
        context["current_date_filter"] = self.request.GET.get('date_filter', '')
        
        # Add filter options
        context["payment_status_choices"] = Deal.PAYMENT_STATUS_CHOICES
        context["deal_status_choices"] = Deal.STATUS_CHOICES
        
        return context

class DealDetailView(LoginRequiredMixin, DetailView):
    model = Deal
    template_name = "deal/deal_details.html"
    context_object_name = "deal"
    pk_url_kwarg = "deal_id"

    def get_object(self, queryset=None):
        return get_object_or_404(Deal.objects.select_related('vehicle_id', 'customer_id'), deal_id=self.kwargs['deal_id'], showroom_id=self.request.user)


@login_required
@require_POST
def send_follow_up(request, deal_id):
    """Send follow-up email/SMS for a specific deal"""
    try:
        deal = get_object_or_404(Deal.objects.select_related('vehicle_id', 'customer_id'), 
                               deal_id=deal_id, showroom_id=request.user)
        
        message_type = request.POST.get('message_type', 'email')
        custom_message = request.POST.get('message', '')
        
        customer = deal.customer_id
        vehicle = deal.vehicle_id
        
        # Generate default message if custom message is not provided
        if not custom_message:
            if message_type == 'email':
                custom_message = f"""
Dear {customer.name},

Following up on your interest in the {vehicle.company} {vehicle.model_name}.

Vehicle Details:
- Model: {vehicle.company} {vehicle.model_name}
- Price: ₹{vehicle.selling_price:,}
- Status: Available

We'd love to discuss this further with you. Please let us know if you have any questions or would like to schedule a test drive.

Best regards,
{request.user.showroom_name if hasattr(request.user, 'showroom_name') else 'Our Team'}
{request.user.phone if hasattr(request.user, 'phone') else 'Contact Number'}
                """
            else:  # SMS
                custom_message = f"Hi {customer.name}, following up on your interest in {vehicle.company} {vehicle.model_name}. Price: ₹{vehicle.selling_price:,}. Call us for details! {request.user.phone if hasattr(request.user, 'phone') else ''}"
        
        success = False
        error_message = ""
        
        if message_type == 'email':
            try:
                send_mail(
                    subject=f'Follow-up: {vehicle.company} {vehicle.model_name}',
                    message=custom_message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@dealtrack.com'),
                    recipient_list=[customer.email],
                    fail_silently=False,
                )
                success = True
            except Exception as e:
                error_message = str(e)
                
        elif message_type == 'sms':
            # For SMS, we'll simulate it (in production, you'd use Twilio or similar)
            try:
                # Simulate SMS sending
                print(f"SMS to {customer.phone}: {custom_message}")
                success = True
            except Exception as e:
                error_message = str(e)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'{message_type.title()} sent successfully to {customer.name}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Failed to send {message_type}: {error_message}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import CreateView
from .forms import DealForm

class DealCreateView(LoginRequiredMixin, CreateView):
    model = Deal
    form_class = DealForm
    template_name = "deal/create_deal.html"
    success_url = reverse_lazy('deal')

    def dispatch(self, request, *args, **kwargs):
        self.vehicle_id = kwargs.get('vehicle_id')
        if self.vehicle_id:
            # Verify vehicle exists and belongs to user's showroom
            self.vehicle = get_object_or_404(Vehicle, vehicle_id=self.vehicle_id, showroom_id=request.user)
            
            # 🔹 SECURITY CHECK: Prevent creating deal for already sold vehicle
            if self.vehicle.is_sold:
                messages.error(request, f"This vehicle ({self.vehicle.company} {self.vehicle.model_name}) is already sold and cannot be sold again.")
                return redirect('vehicle_detail', vehicle_id=self.vehicle.vehicle_id)
                
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicles'] = Vehicle.objects.filter(showroom_id=self.request.user, vehicle_status="Avail")
        context['customer'] = Customer.objects.filter(showroom_id=self.request.user)
        
        # Add pre-selected vehicle to context
        if hasattr(self, 'vehicle'):
            context['selected_vehicle'] = self.vehicle
        return context

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self, 'vehicle'):
            initial['vehicle_id'] = self.vehicle
            # Pre-populate selling price when vehicle is pre-selected
            initial['selling_price'] = self.vehicle.selling_price
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass selected vehicle to form if it exists
        if hasattr(self, 'vehicle'):
            kwargs['selected_vehicle'] = self.vehicle
        return kwargs

    def form_valid(self, form):
        form.instance.showroom_id = self.request.user
        vehicle = form.cleaned_data['vehicle_id']
        
        # 🔹 SECURITY CHECK: Double-check vehicle is not sold
        if vehicle.is_sold:
            messages.error(self.request, f"This vehicle ({vehicle.company} {vehicle.model_name}) is already sold and cannot be sold again.")
            return redirect('vehicle_detail', vehicle_id=vehicle.vehicle_id)
        
        # Calculate financials mathematically based on form inputs
        selling_price = vehicle.selling_price
        discount = form.cleaned_data.get('discount', 0)
        commission = form.cleaned_data.get('commission', 0)
        expenses = form.cleaned_data.get('total_expenses', 0)
        
        final_price = selling_price - discount
        profit = final_price - (commission + expenses)
        
        form.instance.selling_price = selling_price
        form.instance.final_price = final_price
        form.instance.profit = profit
        form.instance.deal_status = "COMPLETED"
        
        response = super().form_valid(form)
        
        # 🔹 Mark vehicle as sold upon successful deal creation
        vehicle.vehicle_status = "sold"
        vehicle.save()
        
        messages.success(self.request, f"Deal created successfully! {vehicle.company} {vehicle.model_name} has been marked as sold.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create deal. Check the inputs.")
        return super().form_invalid(form)
