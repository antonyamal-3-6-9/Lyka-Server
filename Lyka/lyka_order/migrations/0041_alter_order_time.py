# Generated by Django 4.2.1 on 2024-01-06 22:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_order', '0040_alter_order_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 6, 22, 0, 13, 133438, tzinfo=datetime.timezone.utc)),
        ),
    ]