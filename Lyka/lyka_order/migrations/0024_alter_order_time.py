# Generated by Django 4.2.1 on 2023-08-05 20:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0023_alter_order_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 5, 20, 48, 10, 333710, tzinfo=datetime.timezone.utc)),
        ),
    ]
