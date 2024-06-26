from django.db import models
from django.db import models
from lyka_user.models import LykaUser
from django.db.models import Avg



class Customer(models.Model):
    user = models.OneToOneField(LykaUser, on_delete = models.CASCADE)
    cart = models.OneToOneField("lyka_cart.Cart", on_delete=models.SET_NULL, null=True)
    wallet = models.OneToOneField("lyka_payment.Wallet", on_delete=models.CASCADE, null=True)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

class CustomerOtp(models.Model):
    verification_credential = models.CharField(unique=True, max_length=255, null=True)
    code = models.CharField(max_length=9)

class CustomerReview(models.Model):
    product = models.ForeignKey("lyka_products.Product", on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    review = models.TextField(max_length=500)
    rating = models.DecimalField(max_digits=1, decimal_places=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def getRating(self, product):
        try:
            average_rating = CustomerReview.objects.filter(product=product).aggregate(avg_rate=Avg('rating'))['avg_rate']
            return average_rating
        except Exception as e:
            return 0