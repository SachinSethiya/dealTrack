import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("showroom", "0002_showroom_pincode"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "customer_id",
                    models.CharField(editable=False, max_length=20, unique=True),
                ),
                ("name", models.CharField(max_length=150)),
                ("phone", models.CharField(max_length=15)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("id_proof_number", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "showroom_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customers",
                        to="showroom.showroom",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
                "db_table": "customer",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["customer_id"], name="customer_custome_33645c_idx"
                    ),
                    models.Index(fields=["name"], name="customer_name_364ac9_idx"),
                    models.Index(fields=["phone"], name="customer_phone_ea919e_idx"),
                ],
            },
        ),
    ]
