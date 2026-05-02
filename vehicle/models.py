from datetime import date

from django.db import models

# Create your models here.
class Vehicle(models.Model):
    status_choice = [('Avail', 'Available'),
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
    registration_no = models.CharField(max_length=15,unique=True)
    chasis_no = models.CharField(max_length=50,unique=True)
    color = models.CharField(max_length=20)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    vehicle_status= models.CharField(max_length=15,choices=status_choice,default="Avail")
    created_at = models.DateTimeField(auto_now_add=True)
    selling_price = models.DecimalField(max_digits=12,decimal_places=2, default=0.0)
    mileage= models.CharField(max_length=10,null=True,blank=True)
    
    def save(self, *args, **kwargs):
        if not self.vehicle_id:
            last_vehicle = Vehicle.objects.order_by('-created_at').first()
            
            if last_vehicle:
                last_id = int(last_vehicle.vehicle_id[3:])
                new_id = last_id + 1
            else:
                new_id = 1

            self.vehicle_id = f"VEH{new_id:04d}"

        super().save(*args, **kwargs)
    class Meta:
        db_table = "vehicle"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company} {self.model_name} ({self.vehicle_id})"  
    
    @property
    def days_in_inventory(self):
        return (date.today() - self.purchase_date).days
    
    @property
    def is_sold(self):
        return self.vehicle_status == 'sold'
    
class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='vehicle_images/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_images"
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            VehicleImage.objects.filter(
                vehicle=self.vehicle,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.vehicle_id} Image"