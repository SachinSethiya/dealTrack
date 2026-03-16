from django import forms
from .models import vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = vehicle
        fields = '__all__'