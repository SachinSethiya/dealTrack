from django import forms
from django.contrib.auth.models import User
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