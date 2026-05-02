from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'company', 'model_name', 'variant', 'manufacturing_year', 
            'fuel_type', 'transmission', 'km_driven', 'registration_no', 
            'chasis_no', 'color', 'purchase_price', 'purchase_date', 
            'vehicle_status', 'selling_price', 'mileage'
        ]
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Toyota'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Camry'}),
            'variant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. XLE'}),
            'manufacturing_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2021'}),
            'fuel_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Petrol'}),
            'transmission': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Automatic'}),
            'km_driven': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15000'}),
            'registration_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MH12AB1234'}),
            'chasis_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chassis Number'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. White'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle_status': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'mileage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15 kmpl'}),
        }


class VehicleUpdateForm(forms.ModelForm):
    """
    Form specifically for updating existing vehicles.
    Includes validation and proper field handling for editing.
    """
    class Meta:
        model = Vehicle
        fields = [
            'company', 'model_name', 'variant', 'manufacturing_year', 
            'fuel_type', 'transmission', 'km_driven', 'registration_no', 
            'chasis_no', 'color', 'purchase_price', 'purchase_date', 
            'vehicle_status', 'selling_price', 'mileage'
        ]
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Toyota'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Camry'}),
            'variant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. XLE'}),
            'manufacturing_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2021'}),
            'fuel_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Petrol'}),
            'transmission': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Automatic'}),
            'km_driven': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15000'}),
            'registration_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MH12AB1234'}),
            'chasis_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chassis Number'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. White'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle_status': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'mileage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15 kmpl'}),
        }

    def __init__(self, *args, **kwargs):
        super(VehicleUpdateForm, self).__init__(*args, **kwargs)
        # Add field labels and help text for better UX
        self.fields['company'].label = 'Company/Brand'
        self.fields['model_name'].label = 'Model Name'
        self.fields['variant'].label = 'Variant/Trim'
        self.fields['manufacturing_year'].label = 'Manufacturing Year'
        self.fields['fuel_type'].label = 'Fuel Type'
        self.fields['transmission'].label = 'Transmission'
        self.fields['km_driven'].label = 'Kilometers Driven'
        self.fields['registration_no'].label = 'Registration Number'
        self.fields['chasis_no'].label = 'Chassis Number'
        self.fields['color'].label = 'Color'
        self.fields['purchase_price'].label = 'Purchase Price'
        self.fields['purchase_date'].label = 'Purchase Date'
        self.fields['vehicle_status'].label = 'Vehicle Status'
        self.fields['selling_price'].label = 'Selling Price'
        self.fields['mileage'].label = 'Mileage'

    def clean_manufacturing_year(self):
        """Validate manufacturing year is reasonable"""
        year = self.cleaned_data.get('manufacturing_year')
        if year:
            current_year = 2024  # You can make this dynamic
            if year < 1900 or year > current_year + 1:
                raise forms.ValidationError(f"Year must be between 1900 and {current_year + 1}")
        return year

    def clean_km_driven(self):
        """Validate km driven is non-negative"""
        km_driven = self.cleaned_data.get('km_driven')
        if km_driven and km_driven < 0:
            raise forms.ValidationError("Kilometers driven cannot be negative")
        return km_driven

    def clean_purchase_price(self):
        """Validate purchase price is positive"""
        price = self.cleaned_data.get('purchase_price')
        if price and price <= 0:
            raise forms.ValidationError("Purchase price must be greater than 0")
        return price

    def clean_selling_price(self):
        """Validate selling price is non-negative"""
        price = self.cleaned_data.get('selling_price')
        if price and price < 0:
            raise forms.ValidationError("Selling price cannot be negative")
        return price