# Generated by Django 4.2.1 on 2023-08-03 22:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_products', '0021_alter_unit_added_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='added_on',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 3, 22, 42, 42, 482325, tzinfo=datetime.timezone.utc)),
        ),
    ]
