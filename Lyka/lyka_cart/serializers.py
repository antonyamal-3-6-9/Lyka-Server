from rest_framework import serializers
from .models import *
from lyka_products.models import Product, Unit
from lyka_products.serializers import ColorSerializer, VariationsSerializer
import uuid



class Cartserializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Cart
        fields = ["cart_id"]

    def create(self, validated_data):
        c_id = uuid.uuid1()
        cart = Cart.objects.create(cart_id=c_id)
        return cart
    

class CartProductRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["brand", "name", "thumbnail"]

class CartUnitSerializer(serializers.ModelSerializer):
    variant = VariationsSerializer()
    color_code = ColorSerializer()
    product = CartProductRetriveSerializer()
    class Meta:
        model = Unit
        fields = ["variant", "color_code", "product", "stock"]

class CartItemsSerializer(serializers.ModelSerializer):
    unit = CartUnitSerializer()
    class Meta:
        model = CartItems
        fields = "__all__"