# Generated by Django 4.2.1 on 2023-08-04 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_payment', '0004_remove_coupontype_discount_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordertransaction',
            name='wallet',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='transaction_limit',
        ),
        migrations.AlterField(
            model_name='ordertransaction',
            name='ref_no',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='wallet_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
