from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from deal.models import Deal
from expense.models import Expense
from vehicle.models import Vehicle
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
import json
from customer.models import Customer
from django.utils import timezone
from datetime import timedelta

@login_required
def reports(request):
    showroom = request.user
    
    # ------------------ 
    # 1. SALES ANALYTICS & REVENUE TRENDS
    # ------------------
    deals = Deal.objects.filter(showroom_id=showroom, deal_status='COMPLETED')
    
    # Monthly aggregations
    monthly_stats = deals.annotate(
        month=TruncMonth('deal_date')
    ).values('month').annotate(
        sales_count=Count('deal_id'),
        revenue=Sum('final_price'),
        profit=Sum('profit')
    ).order_by('month')

    months = []
    sales_data = []
    revenue_data = []
    profit_data = []

    for stat in monthly_stats:
        mon_str = stat['month'].strftime("%b %Y") if stat['month'] else "Unknown"
        months.append(mon_str)
        sales_data.append(stat['sales_count'])
        revenue_data.append(float(stat['revenue'] or 0))
        profit_data.append(float(stat['profit'] or 0))

    # Overall Profits & Revenue
    total_sales = sum(sales_data)
    total_revenue = sum(revenue_data)
    total_gross_profit = sum(profit_data)

    # ------------------ 
    # 2. EXPENSE ANALYSIS
    # ------------------
    expenses = Expense.objects.filter(showroom_id=showroom)
    expense_stats = expenses.values('expense_type').annotate(total=Sum('amount'))
    
    expense_labels = []
    expense_data = []
    for exp in expense_stats:
        expense_labels.append(exp['expense_type'].title())
        expense_data.append(float(exp['total'] or 0))

    total_expenses = sum(expense_data)
    
    # Net Profit
    net_profit = total_gross_profit - total_expenses
    
    # Profit Per Vehicle (Avg)
    profit_per_vehicle = (net_profit / total_sales) if total_sales > 0 else 0
    
    # Profit Margin %
    profit_margin = ((net_profit / total_revenue) * 100) if total_revenue > 0 else 0

    # ------------------ 
    # 3. INVENTORY STATUS
    # ------------------
    inventory_stats = Vehicle.objects.filter(showroom_id=showroom).values('vehicle_status').annotate(count=Count('vehicle_id'))
    
    inventory_labels = []
    inventory_data = []
    for inv in inventory_stats:
        inventory_labels.append(inv['vehicle_status'].title() if inv['vehicle_status'] else 'Unknown')
        inventory_data.append(inv['count'])

    # ------------------ 
    # 4. ENHANCED ANALYTICS
    # ------------------
    
    # Deal status distribution
    deal_status_stats = Deal.objects.filter(showroom_id=showroom).values('deal_status').annotate(count=Count('deal_id'))
    deal_status_labels = []
    deal_status_data = []
    for status in deal_status_stats:
        deal_status_labels.append(status['deal_status'].title())
        deal_status_data.append(status['count'])
    
    # Payment status distribution
    payment_status_stats = Deal.objects.filter(showroom_id=showroom).values('payment_status').annotate(count=Count('deal_id'))
    payment_status_labels = []
    payment_status_data = []
    for payment in payment_status_stats:
        payment_status_labels.append(payment['payment_status'].title())
        payment_status_data.append(payment['count'])
    
    # Top performing vehicles (by revenue)
    top_vehicles = Deal.objects.filter(showroom_id=showroom, deal_status='COMPLETED')\
        .values('vehicle_id__company', 'vehicle_id__model_name')\
        .annotate(total_revenue=Sum('final_price'), vehicle_count=Count('deal_id'))\
        .order_by('-total_revenue')[:5]
    
    # Calculate average price for each top vehicle
    for vehicle in top_vehicles:
        vehicle['avg_price'] = vehicle['total_revenue'] / vehicle['vehicle_count'] if vehicle['vehicle_count'] > 0 else 0
    
    # Customer analytics
    total_customers = Customer.objects.filter(showroom=showroom).count()
    active_customers = Customer.objects.filter(showroom=showroom, deal__isnull=False).distinct().count()
    
    # Monthly trends (last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    recent_monthly_stats = deals.filter(deal_date__gte=six_months_ago).annotate(
        month=TruncMonth('deal_date')
    ).values('month').annotate(
        sales_count=Count('deal_id'),
        revenue=Sum('final_price'),
        profit=Sum('profit')
    ).order_by('month')
    
    # Calculate growth rates
    if len(recent_monthly_stats) >= 2:
        latest_month = recent_monthly_stats.last()
        previous_month = recent_monthly_stats[len(recent_monthly_stats)-2]
        
        sales_growth = ((latest_month['sales_count'] - previous_month['sales_count']) / previous_month['sales_count'] * 100) if previous_month['sales_count'] > 0 else 0
        revenue_growth = ((latest_month['revenue'] - previous_month['revenue']) / previous_month['revenue'] * 100) if previous_month['revenue'] > 0 else 0
    else:
        sales_growth = 0
        revenue_growth = 0

    # Calculate conversion rate
    conversion_rate = ((active_customers / total_customers) * 100) if total_customers > 0 else 0

    context = {
        # Basic KPIs
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "gross_profit": total_gross_profit,
        "net_profit": net_profit,
        "total_expenses": total_expenses,
        "profit_per_vehicle": profit_per_vehicle,
        "profit_margin": profit_margin,
        
        # Enhanced KPIs
        "total_customers": total_customers,
        "active_customers": active_customers,
        "sales_growth": sales_growth,
        "revenue_growth": revenue_growth,
        "conversion_rate": conversion_rate,
        
        # JSON Strings for Chart.js
        "chart_months": json.dumps(months),
        "chart_sales": json.dumps(sales_data),
        "chart_revenue": json.dumps(revenue_data),
        "chart_profit": json.dumps(profit_data),
        "chart_expense_labels": json.dumps(expense_labels),
        "chart_expense_data": json.dumps(expense_data),
        "chart_inventory_labels": json.dumps(inventory_labels),
        "chart_inventory_data": json.dumps(inventory_data),
        "chart_deal_status_labels": json.dumps(deal_status_labels),
        "chart_deal_status_data": json.dumps(deal_status_data),
        "chart_payment_status_labels": json.dumps(payment_status_labels),
        "chart_payment_status_data": json.dumps(payment_status_data),
        
        # Top vehicles data
        "top_vehicles": top_vehicles,
    }

    return render(request, "reports/reports.html", context)