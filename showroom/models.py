from django.db import models
import uuid
from django.core.validators import RegexValidator
# Create your models here.
class Showroom(models.Model):
    showroom_id = models.CharField(max_length=20, unique=True, editable=False)
    showroom_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pincode')],
        null=True,
        blank=True
    )    
    address = models.TextField()
    gst_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.showroom_id:
            super().save(*args, **kwargs)  # save first to get ID
            self.showroom_id = f"SHR{self.pk:04d}"
            super().save(update_fields=['showroom_id'])
        else:
            super().save(*args, **kwargs)

class Meta:
    db_table = "showroom"
    ordering = ['-created_at']
    verbose_name = "Showroom"
    verbose_name_plural = "Showrooms"
    indexes = [
        models.Index(fields=['showroom_name']),
        models.Index(fields=['city']),
        models.Index(fields=['state']),
    ]
