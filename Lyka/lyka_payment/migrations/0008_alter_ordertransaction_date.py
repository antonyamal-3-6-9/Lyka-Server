# Generated by Django 4.2.1 on 2023-08-07 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyka_payment', '0007_ordertransaction_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordertransaction',
            name='date',
            field=models.DateField(null=True),
        ),
    ]
