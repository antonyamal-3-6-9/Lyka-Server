# Generated by Django 4.2.1 on 2023-08-10 07:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0033_alter_order_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 10, 7, 16, 9, 211292, tzinfo=datetime.timezone.utc)),
        ),
    ]
