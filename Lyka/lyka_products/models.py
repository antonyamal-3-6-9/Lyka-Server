from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from lyka_categories.models import *
from datetime import datetime, timedelta
import uuid

class Details(models.Model):
    product_type = models.OneToOneField(Main, on_delete=models.CASCADE, null=True, blank=True)
    key_features = models.JSONField(default=dict)
    all_details = models.JSONField(default=dict)

def thumbnail_upload_path(instance, filename):
    return f'Thumbnails/{instance.brand}_{instance.name}/{filename}'

class Variations(models.Model):
    variation = models.CharField(max_length=255)

    def __str__(self):
        return self.variation

class Color(models.Model):
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.color
    



def product_image_upload_path(instance, filename):
    return f'Images/Product/{instance.id}/{filename}'
    
class ProductImage(models.Model):
    image = models.ImageField(upload_to=product_image_upload_path, max_length=300) 
    
class Product(models.Model):
    productId = models.UUIDField(primary_key=True)
    brand = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    availability = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_path, null=True)
    weight = models.CharField(max_length=10, null=True)
    description = models.TextField(max_length=1000, null=True)
    details = models.OneToOneField(Details, on_delete=models.SET_NULL, null=True)
    root_category = models.ForeignKey(Root, on_delete=models.DO_NOTHING, null=True)
    main_category = models.ForeignKey(Main, on_delete=models.DO_NOTHING, null=True)
    sub_category = models.ForeignKey(Sub, on_delete=models.DO_NOTHING, null=True)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    launch_date = models.DateField(null=True)
    variations = models.ManyToManyField(Variations)
    colors = models.ManyToManyField(Color)
    images = models.ManyToManyField(ProductImage)

    def __str__(self):
        return f'{self.brand} {self.name}'



    
class Unit(models.Model):
    unit_id = models.UUIDField(primary_key=True, unique=True)
    color_code = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(Variations, on_delete=models.SET_NULL, null=True)
    stock = models.IntegerField(default=0)
    selling_price = models.PositiveIntegerField(default=0)    
    offer_price = models.PositiveIntegerField(default=0)
    original_price = models.PositiveIntegerField(default=0)
    slug = models.SlugField(null=True, max_length=255)
    is_active = models.BooleanField(default=False)
    units_sold = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    seller = models.ForeignKey("lyka_seller.Seller", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    added_on = models.DateTimeField(default=timezone.now())

    def set_slug(self):
        slug = f"{self.product.brand} {self.product.name} {self.variant.variation} {self.color_code.color}"
        base_slug = slugify(slug)
            
        if not Unit.objects.filter(slug=base_slug).exists():
            self.slug = base_slug
        else:
            unique_id = str(uuid.uuid4())[:8] 
            self.slug = f"{base_slug}-{unique_id}"
            self.save()

    def set_discount(self):
        self.discount = self.selling_price - self.offer_price
        self.save()

    def __str__(self):
        return f"#{self.seller.bussiness_name} {self.product.brand} {self.product.name}"



def image_upload_path(instance, filename):
    return f'Images/{instance.product.root_category.name}/{instance.product.main_category.name}/{instance.product.sub_category.name}/{instance.product.brand}_{instance.product.name}_{instance.product.variant}/{filename}'


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null = True, related_name='productimages')
    image = models.ImageField(upload_to=image_upload_path, max_length=300)                            







