from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Payment
from .forms import PaymentForm
from deal.models import Deal
from django.db.models import Sum

# List View
class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payment/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        return Payment.objects.filter(showroom=self.request.user).select_related('deal').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate payment statistics
        payments = self.get_queryset()
        context['total_payments'] = payments.count()
        context['total_amount'] = payments.aggregate(total=Sum('total_amount'))['total'] or 0
        context['total_paid'] = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
        context['remaining_amount'] = context['total_amount'] - context['total_paid']
        return context

# Detail View
class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payment/payment_detail.html'
    context_object_name = 'payment_obj'
    pk_url_kwarg = 'payment_id'
    
    def get_object(self):
        return get_object_or_404(Payment, id=self.kwargs['payment_id'], showroom=self.request.user)

# Create View
@login_required
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.showroom = request.user
            payment.save()
            messages.success(request, f'Payment {payment.id} created successfully!')
            return redirect('payment_detail', payment_id=payment.id)
        else:
            messages.error(request, 'Error creating payment. Please check the form.')
    else:
        form = PaymentForm(user=request.user)
    
    return render(request, 'payment/payment_form.html', {
        'form': form,
        'title': 'Add New Payment',
        'action': 'Create'
    })

# Update View
@login_required
def update_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, showroom=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Payment {payment.id} updated successfully!')
            return redirect('payment_detail', payment_id=payment_id)
        else:
            messages.error(request, 'Error updating payment. Please check the form.')
    else:
        form = PaymentForm(instance=payment, user=request.user)
    
    return render(request, 'payment/payment_form.html', {
        'form': form,
        'payment_obj': payment,
        'title': 'Edit Payment',
        'action': 'Update'
    })

# Delete View
@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, showroom=request.user)
    
    if request.method == 'POST':
        payment_id_str = payment.id
        payment.delete()
        messages.success(request, f'Payment {payment_id_str} deleted successfully!')
        return redirect('payment_list')
    
    return render(request, 'payment/payment_confirm_delete.html', {
        'payment_obj': payment
    })

# Legacy function for backward compatibility
def payment(request):
    return PaymentListView.as_view()(request)