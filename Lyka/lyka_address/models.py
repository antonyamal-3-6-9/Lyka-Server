from django.db import models



# Create your models here.

def store_upload_path(instance, filename):
    return f'Store_Images/{instance.store_name}/{instance.id}/{filename}'


class SellerStoreAddress(models.Model):
    store_name = models.CharField(max_length=50)
    street_one = models.CharField(max_length=255)
    street_two = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    alternate_phone = models.CharField(max_length=10)
    landmark = models.TextField(max_length=100)
    zip_code = models.CharField(max_length=6)
    image = models.ImageField(upload_to=store_upload_path, null=True)



class CustomerAddress(models.Model):
    owner = models.ForeignKey("lyka_customer.Customer", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    street_one = models.CharField(max_length=255)
    street_two = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    alternate_phone = models.CharField(max_length=10)
    landmark = models.TextField(max_length=100)
    zip_code = models.CharField(max_length=6)
    address_type = models.CharField(max_length=25)




