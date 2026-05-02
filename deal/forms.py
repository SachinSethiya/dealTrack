from django import forms
from .models import Deal
from vehicle.models import Vehicle

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['vehicle_id', 'customer_id', 'discount', 'commission', 'total_expenses', 'deal_date', 'payment_status']
        
    def __init__(self, *args, **kwargs):
        selected_vehicle = kwargs.pop('selected_vehicle', None)
        super(DealForm, self).__init__(*args, **kwargs)
        
        # If a vehicle is pre-selected, hide the vehicle field and set it as readonly
        if selected_vehicle:
            self.fields['vehicle_id'].widget = forms.HiddenInput()
            self.fields['vehicle_id'].initial = selected_vehicle
            self.fields['vehicle_id'].disabled = True
        else:
            # Filter vehicles to only show available ones from user's showroom
            self.fields['vehicle_id'].queryset = Vehicle.objects.filter(
                vehicle_status='Avail'
            ).order_by('-created_at')
        
    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get("vehicle_id")
        
        if vehicle and vehicle.vehicle_status == 'sold':
            raise forms.ValidationError("This vehicle has already been sold.")
            
        return cleaned_data
