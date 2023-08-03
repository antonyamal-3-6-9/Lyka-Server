# Generated by Django 4.2.1 on 2023-08-01 14:55

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_seller', '0003_initial'),
        ('lyka_customer', '0004_initial'),
        ('lyka_order', '0008_alter_order_billing_address_alter_order_order_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lyka_customer.customer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lyka_seller.seller'),
        ),
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 1, 14, 55, 55, 912567, tzinfo=datetime.timezone.utc)),
        ),
    ]
