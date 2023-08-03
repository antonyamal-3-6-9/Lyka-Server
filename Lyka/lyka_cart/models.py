from django.db import models
from lyka_products.models import Product , Unit

# Create your models here.

class Cart(models.Model):
    cart_id = models.UUIDField()

    
class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=0, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)

    def item_set(self):
        self.item_price = self.unit.offer_price * self.quantity
        

