# Generated by Django 4.2.1 on 2023-07-28 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lyka_customer', '0002_initial'),
        ('lyka_address', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeraddress',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lyka_customer.customer'),
        ),
    ]
