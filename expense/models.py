from django.db import models


class Expense(models.Model):

    EXPENSE_TYPE_CHOICES = [
        ('repair', 'Repair'),
        ('service', 'Service'),
        ('rto', 'RTO'),
        ('other', 'Other'),
    ]


    expense_id = models.CharField(max_length=10,unique=True,editable=False)
    showroom = models.ForeignKey('showroom.Showroom',on_delete=models.CASCADE)
    vehicle = models.ForeignKey('vehicle.Vehicle',on_delete=models.CASCADE,null=True,blank=True)
    expense_type = models.CharField(max_length=20,choices=EXPENSE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.TextField(blank=True,null=True)
    expense_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        import uuid
        if not self.expense_id:
            self.expense_id = "EXP" + str(uuid.uuid4().hex[:6].upper())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle} - {self.expense_type} - ₹{self.amount}"
    
    class Meta:
        db_table =  "expense"
    