from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("customer", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customer",
            old_name="showroom_id",
            new_name="showroom",
        ),
    ]
