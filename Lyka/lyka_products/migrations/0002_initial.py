# Generated by Django 4.2.1 on 2023-07-28 21:53

import datetime
from django.db import migrations, models
import django.db.models.deletion
import lyka_products.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lyka_products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_features', models.JSONField(default=dict)),
                ('all_details', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=300, upload_to=lyka_products.models.image_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('productId', models.UUIDField(primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('availability', models.BooleanField(default=True)),
                ('thumbnail', models.ImageField(null=True, upload_to=lyka_products.models.thumbnail_upload_path)),
                ('weight', models.CharField(max_length=10, null=True)),
                ('description', models.TextField(max_length=1000, null=True)),
                ('average_rating', models.DecimalField(decimal_places=1, max_digits=2, null=True)),
                ('launch_date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=300, upload_to=lyka_products.models.product_image_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='Variations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variation', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('unit_id', models.UUIDField(primary_key=True, serialize=False, unique=True)),
                ('stock', models.IntegerField(default=0)),
                ('selling_price', models.PositiveIntegerField(default=0)),
                ('offer_price', models.PositiveIntegerField(default=0)),
                ('original_price', models.PositiveIntegerField(default=0)),
                ('slug', models.SlugField(max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('units_sold', models.PositiveIntegerField(default=0)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('added_on', models.DateTimeField(default=datetime.datetime(2023, 7, 28, 21, 53, 32, 101607, tzinfo=datetime.timezone.utc))),
                ('color_code', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lyka_products.color')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lyka_products.product')),
            ],
        ),
    ]
