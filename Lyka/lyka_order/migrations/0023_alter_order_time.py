# Generated by Django 4.2.1 on 2023-08-05 20:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0022_alter_order_time_alter_ordercredentials_payment_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 5, 20, 36, 26, 184848, tzinfo=datetime.timezone.utc)),
        ),
    ]
