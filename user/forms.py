from django import forms
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'role', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Full Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone'].label = 'Phone Number'
        self.fields['role'].label = 'Role'
        self.fields['is_active'].label = 'Active'
        
        # Make password optional for updates
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['password'].help_text = "Leave blank to keep current password"
        else:
            self.fields['password'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Handle password
        if self.cleaned_data.get('password'):
            from django.contrib.auth.hashers import make_password
            user.password = make_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        return user
