# Generated by Django 4.2.1 on 2023-08-04 23:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_seller', '0003_initial'),
        ('lyka_products', '0023_alter_unit_added_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lyka_seller.pickupstore'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='added_on',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 4, 23, 23, 43, 533060, tzinfo=datetime.timezone.utc)),
        ),
    ]
