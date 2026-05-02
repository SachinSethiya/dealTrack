from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, URLValidator
from .models import Showroom

class ShowroomSignupForm(forms.ModelForm):
    # Authentication fields
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = Showroom
        fields = [
            'showroom_name', 'owner_name', 'email', 'phone_number',
            'state', 'city', 'pincode', 'address', 'gst_number'
        ]

    def save(self, commit=True):
        # 1. Create the User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )

        # 2. Create Showroom linked to this user
        showroom = super().save(commit=False)
        showroom.user = user
        if commit:
            showroom.save()
        return showroom


class ShowroomSettingsForm(forms.ModelForm):
    """
    Comprehensive form for updating Showroom (User) profile and settings.
    Handles all fields from the Showroom model that are relevant to settings.
    """
    
    # Additional validation for specific fields
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Profile image with validation
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-sm',
            'accept': 'image/*'
        })
    )
    
    # Primary brand color
    primary_color = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-color',
            'type': 'color'
        })
    )

    class Meta:
        model = Showroom
        fields = [
            'username', 'email', 'showroom_name', 'owner_name', 'phone_number', 
            'address', 'city', 'state', 'pincode', 'gst_number', 
            'business_type', 'image', 'primary_color'
        ]
        widgets = {
            'showroom_name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'resize: none;'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have proper form-control class and remove required attributes
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            # Explicitly remove required attribute to prevent browser validation
            field.widget.attrs.pop('required', None)
            # Ensure field is not required
            field.required = False

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        # Only validate if email is provided (not empty)
        if email and email.strip():
            if Showroom.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        # Only validate if username is provided (not empty)
        if username and username.strip():
            if Showroom.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_image(self):
        """Validate profile image"""
        image = self.cleaned_data.get('image')
        if image:
            # Validate file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB.")
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            file_extension = image.name.split('.')[-1].lower()
            if file_extension not in valid_extensions:
                raise forms.ValidationError("Only JPG, JPEG, PNG, GIF, and WebP files are allowed.")
        
        return image

    def clean_primary_color(self):
        """Validate primary color format"""
        color = self.cleaned_data.get('primary_color')
        if color:
            # Ensure it's a valid hex color
            if not color.startswith('#') or len(color) not in [4, 7]:
                raise forms.ValidationError("Please enter a valid hex color (e.g., #2563eb).")
        return color