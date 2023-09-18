# Generated by Django 4.2.1 on 2023-08-07 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_payment', '0005_remove_ordertransaction_wallet_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesreport',
            name='sales_by_customer',
        ),
        migrations.AddField(
            model_name='ordertransaction',
            name='profit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='ordertransaction',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='salesreport',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AddField(
            model_name='salesreport',
            name='total_products_sold',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='salesreport',
            name='total_profit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salesreport',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='salesreport',
            name='start_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='salesreport',
            name='total_sales',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
