from django import forms
from django.contrib.auth.password_validation import validate_password
from showroom.models import Showroom
from .models import AdminSettings


class ShowroomCreationForm(forms.ModelForm):
    """
    Dynamic ModelForm for creating Showroom instances.
    Automatically includes all required fields from the Showroom model.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text="Enter a secure password for the showroom account"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Confirm the password"
    )
    
    class Meta:
        model = Showroom
        # Include all fields except auto-generated and system fields
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'showroom_name', 'owner_name', 'phone_number',
            'address', 'city', 'state', 'pincode',
            'gst_number', 'business_type', 'image', 'primary_color'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'showroom_name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set field labels and help text
        self.fields['username'].label = 'Username'
        self.fields['username'].help_text = 'Unique username for the showroom account'
        
        self.fields['email'].label = 'Email Address'
        self.fields['email'].help_text = 'Business email address'
        
        self.fields['showroom_name'].label = 'Showroom Name'
        self.fields['showroom_name'].help_text = 'Official name of the showroom'
        
        self.fields['owner_name'].label = 'Owner Name'
        self.fields['owner_name'].help_text = 'Full name of the showroom owner'
        
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['phone_number'].help_text = 'Contact phone number'
        
        self.fields['address'].label = 'Address'
        self.fields['address'].help_text = 'Complete business address'
        
        self.fields['city'].label = 'City'
        self.fields['city'].help_text = 'City where showroom is located'
        
        self.fields['state'].label = 'State'
        self.fields['state'].help_text = 'State where showroom is located'
        
        self.fields['pincode'].label = 'Pincode'
        self.fields['pincode'].help_text = 'Postal code'
        
        self.fields['gst_number'].label = 'GST Number'
        self.fields['gst_number'].help_text = 'GST identification number (optional)'
        self.fields['gst_number'].required = False
        
        self.fields['business_type'].label = 'Business Type'
        self.fields['business_type'].help_text = 'Type of business (e.g., Car Dealer, Bike Dealer)'
        self.fields['business_type'].required = False
        
        self.fields['image'].label = 'Profile Image'
        self.fields['image'].help_text = 'Showroom logo or profile picture (optional)'
        self.fields['image'].required = False
        
        self.fields['primary_color'].label = 'Theme Color'
        self.fields['primary_color'].help_text = 'Primary theme color for the showroom'
        
        # Set required fields based on model
        required_fields = ['username', 'email', 'password', 'confirm_password', 
                          'showroom_name', 'owner_name', 'phone_number']
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_confirm_password(self):
        """Validate that password and confirm_password match"""
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return confirm_password
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email and Showroom.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        if username and Showroom.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def save(self, commit=True):
        """
        Save the showroom instance with proper password handling.
        Uses Django's create_user method for proper password hashing.
        """
        # Get cleaned data
        cleaned_data = self.cleaned_data
        password = cleaned_data.pop('password', None)
        confirm_password = cleaned_data.pop('confirm_password', None)
        
        # Create showroom instance without password
        showroom = super().save(commit=False)
        
        # Set password using Django's create_user method
        if password:
            showroom.set_password(password)
        
        # Set is_active to True by default
        showroom.is_active = True
        showroom.is_superuser = False
        showroom.is_staff = False
        
        if commit:
            showroom.save()
        
        return showroom


class AdminSettingsForm(forms.ModelForm):
    """
    Form for updating platform-wide admin settings.
    """
    class Meta:
        model = AdminSettings
        fields = [
            'allow_new_showroom_registration',
            'maintenance_mode', 
            'platform_announcement',
            'max_showrooms_per_user',
            'email_notifications_enabled'
        ]
        widgets = {
            'allow_new_showroom_registration': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'platform_announcement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_showrooms_per_user': forms.NumberInput(attrs={'class': 'form-control'}),
            'email_notifications_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['allow_new_showroom_registration'].label = 'Allow New Showroom Registration'
        self.fields['allow_new_showroom_registration'].help_text = 'Enable/disable new user registration'
        
        self.fields['maintenance_mode'].label = 'Maintenance Mode'
        self.fields['maintenance_mode'].help_text = 'Put the platform in maintenance mode'
        
        self.fields['platform_announcement'].label = 'Platform Announcement'
        self.fields['platform_announcement'].help_text = 'Display announcement to all users'
        
        self.fields['max_showrooms_per_user'].label = 'Max Showrooms Per User'
        self.fields['max_showrooms_per_user'].help_text = 'Maximum showrooms a user can create'
        
        self.fields['email_notifications_enabled'].label = 'Email Notifications'
        self.fields['email_notifications_enabled'].help_text = 'Enable email notifications'


class AdminPasswordChangeForm(forms.Form):
    """
    Form for changing admin password.
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password",
        validators=[validate_password]
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm New Password"
    )
    
    def clean_confirm_new_password(self):
        """Validate that new passwords match"""
        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("New passwords do not match")
        
        return confirm_new_password
    
    def clean_current_password(self):
        """Validate current password"""
        current_password = self.cleaned_data.get('current_password')
        if not current_password:
            raise forms.ValidationError("Please enter your current password")
        return current_password
