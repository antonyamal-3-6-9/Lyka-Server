# Generated by Django 4.2.1 on 2023-08-01 17:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0009_alter_order_customer_alter_order_seller_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_list',
        ),
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 1, 17, 18, 40, 503389, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='OrderList',
        ),
    ]
