# Generated by Django 4.2.1 on 2023-08-07 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_payment', '0006_remove_salesreport_sales_by_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordertransaction',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
