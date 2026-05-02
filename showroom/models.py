from django.db import models
from django.contrib.auth.models import AbstractUser

class Showroom(AbstractUser):

    # Basic business info
    showroom_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=150)
    # Contact information
    phone_number     = models.CharField(max_length=20)
    email = models.EmailField()
    # Address details
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    # Business information
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="showroomAdmin/",default='showroomAdmin/user-profile')
    primary_color = models.CharField(max_length=10, default="#2563eb")
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = "showroomUser"