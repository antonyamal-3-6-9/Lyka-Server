# Generated by Django 4.2.1 on 2023-08-04 23:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0020_alter_order_options_alter_order_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_charge',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ordergroup',
            name='total_shipping_charge',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 4, 23, 23, 43, 528059, tzinfo=datetime.timezone.utc)),
        ),
    ]
