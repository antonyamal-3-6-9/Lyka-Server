from django.db import models
from lyka_customer.models import Customer
from lyka_address.models import *
from lyka_products.models import *
from django.utils import timezone
import json


class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    limit = models.DecimalField(max_digits=10, decimal_places=2)

class OrderCredentials(models.Model):
    shipping_partner_order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    tracking_id = models.CharField(max_length=100)

class OrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product_price = models.PositiveIntegerField()
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_variant = models.ForeignKey(Variations, on_delete=models.SET_NULL, null=True)
    product_color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def set_selling_price(self):
        self.selling_price = self.selling_price * self.quantity

    def get_tax_price(self, rate, product_price, quatity):
        return (((product_price * rate) / 100) * quatity) 

    def set_tax_price(self):
        taxes = Tax.objects.filter(limit__lt=self.product_price)
        if not taxes:
            self.product_price * self.quantity
        tax_price = 0
        for tax in taxes:
            tax_price += self.get_tax_price(tax.rate, self.product_price, self.quantity)
        self.product_price = ((self.product_price * self.quantity)  + tax_price)
        self.additional_charges = tax_price


class OrderGroup(models.Model):
    order_list_id = models.UUIDField(primary_key=True, unique=True)
    total_price = models.PositiveIntegerField(default=0)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)

    def set_total_price(self):
        orders = Order.objects.filter(order_list=self.order_list_id)
        self.total_price = 0
        self.additional_charges = 0
        self.discount = 0
        self.total_selling_price = 0
        self.coupon_discount = 0 
        for order in orders:
            self.total_price = self.total_price + order.item.product_price
            self.additional_charges = self.additional_charges + order.item.additional_charges
            self.total_selling_price = self.total_selling_price + order.item.selling_price
            self.discount = self.discount + order.item.discount
            self.coupon_discount = self.coupon_discount + order.item.coupon_discount


class Order(models.Model):
    order_list = models.ForeignKey(OrderGroup, on_delete=models.CASCADE, null=True)
    order_id = models.UUIDField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    seller = models.ForeignKey("lyka_seller.Seller", on_delete=models.CASCADE, null=True)
    item = models.OneToOneField(OrderItems, on_delete=models.CASCADE, null=True)
    pickup_address = models.ForeignKey(SellerStoreAddress, on_delete=models.CASCADE, null=True)
    order_status = models.CharField(max_length=50, null=True)
    payment_status = models.BooleanField(default=False)
    billing_address = models.ForeignKey(CustomerAddress, on_delete=models.CASCADE, related_name="bill_add", null=True)
    shipping_address = models.ForeignKey(CustomerAddress, on_delete=models.CASCADE, related_name="ship_add", null=True)
    credentials = models.OneToOneField(OrderCredentials, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField(default=timezone.now())
    payment_method = models.CharField(max_length=50, null=True)



