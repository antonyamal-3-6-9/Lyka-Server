# Generated by Django 4.2.1 on 2023-07-28 21:53

from django.db import migrations, models
import lyka_address.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lyka_address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('street_one', models.CharField(max_length=255)),
                ('street_two', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=10)),
                ('alternate_phone', models.CharField(max_length=10)),
                ('landmark', models.TextField(max_length=100)),
                ('zip_code', models.CharField(max_length=6)),
                ('address_type', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='SellerStoreAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=50)),
                ('street_one', models.CharField(max_length=255)),
                ('street_two', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=10)),
                ('alternate_phone', models.CharField(max_length=10)),
                ('landmark', models.TextField(max_length=100)),
                ('zip_code', models.CharField(max_length=6)),
                ('image', models.ImageField(null=True, upload_to=lyka_address.models.store_upload_path)),
            ],
        ),
    ]
