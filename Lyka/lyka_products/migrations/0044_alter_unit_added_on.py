# Generated by Django 4.2.1 on 2024-01-06 22:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_products', '0043_alter_unit_added_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='added_on',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 6, 22, 0, 13, 125428, tzinfo=datetime.timezone.utc)),
        ),
    ]
