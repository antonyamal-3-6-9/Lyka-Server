# Generated by Django 4.2.1 on 2023-08-01 22:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0015_alter_order_time_alter_tax_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 1, 22, 8, 58, 390328, tzinfo=datetime.timezone.utc)),
        ),
    ]
