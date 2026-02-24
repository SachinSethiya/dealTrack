from django.db import models

class Deal(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
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

    profit = models.DecimalField(max_digits=12, decimal_places=2)

    deal_date = models.DateField()
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.deal_id