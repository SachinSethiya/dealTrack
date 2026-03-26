from django.db import models
import uuid

class Deal(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Open'),           # deal created
        ('COMPLETED', 'Completed'), # deal finished
        ('CANCELLED', 'Cancelled'), # optional
    ]

    deal_id = models.CharField(max_length=10,primary_key=True,editable=False)
    showroom_id = models.ForeignKey('showroom.Showroom',on_delete=models.CASCADE,db_column='showroom_id')
    vehicle_id = models.ForeignKey('vehicle.Vehicle',on_delete=models.CASCADE,db_column='vehicle_id')
    customer_id = models.ForeignKey('customer.Customer',on_delete=models.PROTECT,db_column='customer_id')

    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=12, decimal_places=2)

    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deal_status = models.CharField(max_length=10,choices=STATUS_CHOICES,default="OPEN")
    profit = models.DecimalField(max_digits=12, decimal_places=2)

    deal_date = models.DateField()
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.deal_id:
            self.deal_id = "DEAL" + str(uuid.uuid4().hex[:6].upper())
        super().save(*args, **kwargs)
    def __str__(self):
        return self.deal_id
    class Meta:
        db_table =  "deal"