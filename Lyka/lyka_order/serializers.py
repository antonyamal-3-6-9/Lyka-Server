from rest_framework import serializers
from .models import *
from lyka_products.serializers import ProductRetriveSerializer, ColorSerializer, VariationsSerializer
from lyka_address.serializers import CustomerAddressRetriveSerializer, SellerStoreAddressRetriveSerializer
from lyka_payment.serializers import CouponSerializer
import uuid
from lyka_seller.serializers import SellerBusinessNameSerializer



class OrderCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCredentials
        fields = "__all__"

class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Order
        fields = ["order_id"]

    def create(self, validated_data):
        o_id = uuid.uuid1()
        order = Order.objects.create(order_id=o_id)
        return order

class OrderGroupSerializer(serializers.ModelSerializer):
    order_list_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = OrderGroup
        fields = ["order_list_id"]

    def create(self, validated_data):
        o_l_id = uuid.uuid1()
        order = OrderGroup.objects.create(order_list_id=o_l_id)
        return order

class OrderItemsRetriveSerializer(serializers.ModelSerializer):
    product = ProductRetriveSerializer()
    product_color = ColorSerializer()
    product_variant = VariationsSerializer()
    class Meta:
        model = OrderItems
        fields = "__all__"

class OrderRetriveSerializer(serializers.ModelSerializer):
    item = OrderItemsRetriveSerializer()
    shipping_address = CustomerAddressRetriveSerializer()
    seller = SellerBusinessNameSerializer()
    class Meta:
        model = Order
        fields = "__all__"


class OrderDetailsRetriveSerializer(serializers.ModelSerializer):
    item = OrderItemsRetriveSerializer()
    shipping_address = CustomerAddressRetriveSerializer()
    billing_address = CustomerAddressRetriveSerializer()
    credentials = OrderCredentialsSerializer()
    pickup_address = SellerStoreAddressRetriveSerializer()
    applied_coupon = CouponSerializer()
    class Meta:
        model = Order
        fields = "__all__"





class OrderGroupPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderGroup
        fields = ["total_price", "total_selling_price", "additional_charges", "coupon_discount", "discount", "total_shipping_charge"]


class OrderItemsPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ["product_price", "selling_price", "coupon_discount", "discount", "additional_charges"]

class OrderPriceSerializer(serializers.ModelSerializer):
    item = OrderItemsPriceSerializer()
    class Meta:
        model = Order
        fields = ["item", "shipping_charge"]

