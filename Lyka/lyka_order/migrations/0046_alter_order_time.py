# Generated by Django 4.2.9 on 2024-01-09 20:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0045_alter_order_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 9, 20, 25, 53, 958052, tzinfo=datetime.timezone.utc)),
        ),
    ]
