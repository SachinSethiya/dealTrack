from django.db import models

# Create your models here.
class vehicle(models.Model):
    status_choice = [('avail', 'Available'),
                    ('sold', 'Sold'),
                    ('reser','Reserved')
                    ]
    vehicle_id = models.CharField(max_length=20,primary_key=True,editable=False)
    showroom_id = models.ForeignKey('showroom.Showroom',on_delete=models.CASCADE,related_name="vehicles")
    company = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    variant = models.CharField(max_length=100)
    manufacturing_year = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    km_driven = models.PositiveIntegerField()
    registration_no = models.CharField(max_length=10,unique=True)
    chasis_no = models.CharField(max_length=50,unique=True)
    color = models.CharField(max_length=20)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    vehicle_status= models.CharField(max_length=15,choices=status_choice,default="Avail")
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Meta:
    db_table = "vehicle"
    ordering = ['-created_at']

def __str__(self):
    return f"{self.company} {self.model_name} ({self.vehicle_id})"    
    
