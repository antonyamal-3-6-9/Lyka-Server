# Generated by Django 4.2.1 on 2023-08-01 14:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0006_alter_order_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderlist',
            name='id',
        ),
        migrations.AddField(
            model_name='orderitems',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderlist',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 1, 14, 53, 13, 540580, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='additional_charges',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='coupon_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderlist',
            name='additional_charges',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderlist',
            name='coupon_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderlist',
            name='order_list_id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
    ]
