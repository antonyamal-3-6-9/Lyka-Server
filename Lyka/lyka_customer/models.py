from django.db import models
from django.db import models
from lyka_user.models import LykaUser
import uuid


class Customer(models.Model):
    user = models.OneToOneField(LykaUser, on_delete = models.CASCADE)
    cart = models.OneToOneField("lyka_cart.Cart", on_delete=models.SET_NULL, null=True)
    wallet = models.OneToOneField("lyka_payment.Wallet", on_delete=models.CASCADE, null=True)
    is_verified = models.BooleanField(default=False)

class CustomerOtp(models.Model):
    verification_credential = models.CharField(unique=True, max_length=255, null=True)
    code = models.CharField(max_length=9)

class CustomerReview(models.Model):
    product = models.ForeignKey("lyka_products.Product", on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    review = models.TextField(max_length=500)
    rating = models.DecimalField(max_digits=1, decimal_places=0)
    
