from django.db import models

PAYMENT_CHOICES = [
    ("CASH", "Cash"),
    ("CARD", "Credit/Debit Card"),
    ("UPI", "UPI"),
    ("NET", "Net Banking"),
    ("WALLET", "Wallet"),
    ("COD", "Cash on Delivery"),
]

class Payment(models.Model):

    id = models.CharField(max_length=10, primary_key=True)

    showroom = models.ForeignKey(
        "showroom.Showroom",
        on_delete=models.CASCADE,
        related_name="payments"
    )

    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        related_name="payments"
    )

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="CASH"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining_amount(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"Payment {self.id}"
    class Meta:
        db_table =  "payment"