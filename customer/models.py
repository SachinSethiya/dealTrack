from django.db import models

# Create your models here.
from django.db import models


class Showroom(models.Model):
    showroom_name = models.CharField(max_length=255)

    def __str__(self):
        return self.showroom_name


class Customer(models.Model):
    showroom = models.ForeignKey(
        Showroom,
        on_delete=models.CASCADE,
        related_name="customers"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    id_proof_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "customers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"
