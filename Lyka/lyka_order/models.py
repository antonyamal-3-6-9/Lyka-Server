from django.db import models
from lyka_customer.models import Customer
from lyka_address.models import *
from lyka_products.models import *
from django.utils import timezone
import json


class Tax(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True, null=True)

class OrderCredentials(models.Model):
    shipping_partner_order_id = models.CharField(max_length=100, null=True)
    payment_id = models.CharField(max_length=100, null=True)
    tracking_id = models.CharField(max_length=100, null=True)

class OrderItems(models.Model):
    product = models.ForeignKey('lyka_products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product_price = models.PositiveIntegerField()
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_variant = models.ForeignKey('lyka_products.Variations', on_delete=models.SET_NULL, null=True)
    product_color = models.ForeignKey('lyka_products.Color', on_delete=models.SET_NULL, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def set_selling_price(self):
        self.selling_price = self.selling_price * self.quantity
        self.discount = self.discount * self.quantity
        self.original_price = self.original_price * self.quantity

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
    applied_coupon = models.ForeignKey("lyka_payment.CouponType", on_delete=models.SET_NULL, null=True)
    total_shipping_charge = models.PositiveIntegerField(default=0)

    def set_total_price(self):
        orders = Order.objects.filter(order_list=self.order_list_id)
        self.total_price = 0
        self.additional_charges = 0
        self.discount = 0
        self.total_selling_price = 0
        self.coupon_discount = 0
        self.total_shipping_charge = 0
        for order in orders:
            self.total_price = self.total_price + order.item.product_price
            self.additional_charges = self.additional_charges + order.item.additional_charges
            self.total_selling_price = self.total_selling_price + order.item.selling_price
            self.discount = self.discount + order.item.discount
            self.coupon_discount = self.coupon_discount + order.item.coupon_discount
            self.total_shipping_charge = self.total_shipping_charge + order.shipping_charge


class Order(models.Model):

    CREATED = 'CREATED'
    PLACED = 'PLACED'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    PICKED_UP = 'PICKED UP'
    SHIPPED = 'SHIPPED'
    IN_TRANSIST = 'IN TRANSIST'
    OUT_OF_DELIVERY = 'OUT OF DELIVERY'
    DELIVERED = 'DELIVERED'
    CANCELATION_REQUESTED = 'CANCELLATION REQUESTED'
    CANCELLED = 'CANCELLED'

    RETURN_REQUESTED = "RETURN REQUESTED"
    RETURN_IN_TRANSIST = "RETURN IN TRANSIST"
    RETURNED = "RETURNED"

    STATUS = [
        (CREATED, 'CREATED'),
        (PLACED, 'PLACED'),
        (CONFIRMED, 'CONFIRMED'),
        (REJECTED, 'REJECTED'),
        (PICKED_UP, 'PICKED UP'),
        (SHIPPED, 'SHIPPED'),
        (IN_TRANSIST, 'IN TRANSIST'),
        (OUT_OF_DELIVERY, 'OUT OF DELIVERY'),
        (DELIVERED, 'DELIVERED')
    ]

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
    applied_coupon = models.ForeignKey("lyka_payment.CouponType", on_delete=models.SET_NULL, null=True)
    shipping_charge = models.PositiveIntegerField(default=0)
    delivery_date = models.DateField(null=True)
    status = models.CharField(choices=STATUS, default=CREATED)

    class Meta:
        ordering = ['time']



