from django import forms
from .models import Expense
from vehicle.models import Vehicle

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'expense_date', 'description', 'vehicle']
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter amount'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description (optional)'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter vehicles by user's showroom
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(showroom_id=user)
        
        # Add empty choice for general expenses
        self.fields['vehicle'].choices = [('', '--- General Expense (No Vehicle) ---')] + list(self.fields['vehicle'].choices)
        
        # Set initial date to today
        if not self.instance.pk:
            from datetime import date
            self.fields['expense_date'].initial = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0.')
        
        return cleaned_data
    
    def clean_expense_date(self):
        expense_date = self.cleaned_data.get('expense_date')
        if expense_date:
            from datetime import date
            if expense_date > date.today():
                raise forms.ValidationError('Expense date cannot be in the future.')
        return expense_date
