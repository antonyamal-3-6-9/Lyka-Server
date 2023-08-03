# Generated by Django 4.2.1 on 2023-08-02 11:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0016_alter_order_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='ordergroup',
            name='total_selling_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='selling_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 2, 11, 17, 24, 547130, tzinfo=datetime.timezone.utc)),
        ),
    ]
