# Generated by Django 4.2.1 on 2023-08-04 13:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_products', '0022_alter_unit_added_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='added_on',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 4, 13, 8, 19, 122034, tzinfo=datetime.timezone.utc)),
        ),
    ]
