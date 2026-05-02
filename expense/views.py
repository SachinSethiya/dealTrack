from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Expense
import uuid
from .forms import ExpenseForm

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = "expense/expense.html"
    context_object_name = "expenses"
    paginate_by = 15

    def get_queryset(self):
        showroom = self.request.user
        queryset = Expense.objects.select_related('vehicle').filter(showroom=showroom)
        
        # Apply GET Filters
        category = self.request.GET.get('category')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        vehicle_id = self.request.GET.get('vehicle_id')

        if category:
            queryset = queryset.filter(expense_type=category)
        if date_from:
            queryset = queryset.filter(expense_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(expense_date__lte=date_to)
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)

        return queryset.order_by('-expense_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from vehicle.models import Vehicle
        context["vehicles"] = Vehicle.objects.filter(showroom_id=self.request.user)
        context["categories"] = Expense.EXPENSE_TYPE_CHOICES
        context["filters"] = self.request.GET
        
        # Calculate statistics
        expenses = self.get_queryset()
        context["total_expenses"] = expenses.count()
        context["vehicle_expenses"] = expenses.filter(vehicle__isnull=False).count()
        context["showroom_expenses"] = expenses.filter(vehicle__isnull=True).count()
        context["total_amount"] = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        return context

class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = "expense/expense_detail.html"
    context_object_name = "expense_obj"
    pk_url_kwarg = 'expense_id'
    
    def get_object(self):
        return get_object_or_404(Expense, expense_id=self.kwargs['expense_id'], showroom=self.request.user)

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expense/expense_form.html"
    pk_url_kwarg = 'expense_id'
    
    def get_object(self):
        return get_object_or_404(Expense, expense_id=self.kwargs['expense_id'], showroom=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('expense_detail', kwargs={'expense_id': self.object.expense_id})
    
    def form_valid(self, form):
        messages.success(self.request, f'Expense {self.object.expense_id} updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error updating expense. Please check the form.')
        return super().form_invalid(form)

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = "expense/expense_confirm_delete.html"
    context_object_name = "expense_obj"
    pk_url_kwarg = 'expense_id'
    success_url = reverse_lazy('expense')
    
    def get_object(self):
        return get_object_or_404(Expense, expense_id=self.kwargs['expense_id'], showroom=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        expense_obj = self.get_object()
        expense_id = expense_obj.expense_id
        messages.success(request, f'Expense {expense_id} deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expense/expense_form.html"
    success_url = reverse_lazy('expense')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.showroom = self.request.user
        form.instance.expense_id = "EXP" + str(uuid.uuid4().hex[:6].upper())
        messages.success(self.request, f'Expense {form.instance.expense_id} created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error creating expense. Please check the form.')
        return super().form_invalid(form)

@login_required
def add_expense(request):
    """Legacy function for backward compatibility"""
    if request.method == "POST":
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense_obj = form.save(commit=False)
            expense_obj.showroom = request.user
            expense_obj.expense_id = "EXP" + str(uuid.uuid4().hex[:6].upper())
            expense_obj.save()
            messages.success(request, "Expense added successfully!")
        else:
            messages.error(request, "Error adding expense. Please check input values.")
        return redirect("expense")
    return redirect("create_expense")