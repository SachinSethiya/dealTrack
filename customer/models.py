from django.db import models

# Create your models here.
from django.db import models


class Customer(models.Model):
    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    showroom = models.ForeignKey("showroom.Showroom", on_delete=models.CASCADE,related_name="customers")
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    id_proof_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            super().save(*args, **kwargs)
            self.customer_id = f"CUS{self.pk:05d}"
            super().save(update_fields=['customer_id'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.name}"

    class Meta:
        db_table = "customer"
        ordering = ['-created_at']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['name']),
            models.Index(fields=['phone']),
        ]