from django.db import models

class User(models.Model):

    user_id = models.AutoField(primary_key=True)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('sales', 'Sales'),
        ('accountant', 'Accountant'),
    ]

    showroom = models.ForeignKey('showroom.Showroom',on_delete=models.CASCADE,related_name='users')

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    password = models.CharField(max_length=255)

    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='sales')

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"



