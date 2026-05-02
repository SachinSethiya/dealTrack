from django import forms
from .models import Payment
from deal.models import Deal

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['deal', 'total_amount', 'amount_paid', 'payment_mode']
        widgets = {
            'deal': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        
        # Filter deals by user's showroom
        if user:
            self.fields['deal'].queryset = Deal.objects.filter(
                showroom_id=user,
                deal_status='COMPLETED'
            ).order_by('-created_at')
        
        self.fields['deal'].label = 'Select Deal'
        self.fields['total_amount'].label = 'Total Amount'
        self.fields['amount_paid'].label = 'Amount Paid'
        self.fields['payment_mode'].label = 'Payment Mode'
    
    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get('total_amount')
        amount_paid = cleaned_data.get('amount_paid')
        
        if total_amount and amount_paid:
            if amount_paid > total_amount:
                raise forms.ValidationError("Amount paid cannot exceed total amount")
        
        return cleaned_data
    
    def save(self, commit=True):
        payment = super().save(commit=False)
        
        # Generate payment ID if not exists
        if not payment.id:
            import uuid
            payment.id = "PAY" + str(uuid.uuid4().hex[:6].upper())
        
        if commit:
            payment.save()
        return payment
