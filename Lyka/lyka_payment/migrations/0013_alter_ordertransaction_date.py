# Generated by Django 4.2.9 on 2024-01-20 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_payment', '0012_salesreport_total_amount_refunded_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordertransaction',
            name='date',
            field=models.DateField(auto_now_add=True, db_index=True, null=True),
        ),
    ]