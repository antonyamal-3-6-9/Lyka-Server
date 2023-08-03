from rest_framework import serializers
from .models import *
from lyka_seller.models import Seller
from django.utils.dateparse import parse_date
from lyka_categories.serializers import *
from lyka_seller.serializers import SellerBusinessNameSerializer
from lyka_user.models import LykaUser
from rest_framework.exceptions import ValidationError
import uuid

class ImageSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField())
    def create(self, validated_data):
        product = self.context['product']  
        images_data = validated_data.pop('images')
        for image_data in images_data:
            Image.objects.create(product=product, image=image_data)
        return product

    
class ImageRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

class CDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details
        fields = "__all__"

class PDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details
        fields = ["key_features", "all_details"]

class VariationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variations
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'





class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductVariationGetSerializer(serializers.ModelSerializer):
    variations = VariationsSerializer(many=True)
    colors = ColorSerializer(many=True)
    class Meta:
        model = Product
        fields = ["variations", "colors"]

class ProductAddSerializer(serializers.ModelSerializer):
    productId = serializers.UUIDField(read_only=True)
    class Meta:
        model = Product
        fields = ["productId", "brand", "name", "root_category", "main_category",
                  "sub_category", "weight", "thumbnail", "launch_date", "description"]
        
    def create(self, validated_data):
        p_id = uuid.uuid1()
        product = Product.objects.create(productId=p_id, **validated_data)
        return product

class ProductAddDetailsSerializer(serializers.ModelSerializer):
    details = PDetailsSerializer()

    class Meta:
        model = Product
        fields = ["details"]

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details")

        details_serializer = PDetailsSerializer(data=details_data)
        details_serializer.is_valid(raise_exception=True)
        details = details_serializer.save()

        instance.details = details
        instance.save()

        return instance
    
class ProductRetriveSerializer(serializers.ModelSerializer):
    root_category = RootViewSerializer()
    main_category = MainViewSerializer()
    sub_category = SubViewSerializer()
    class Meta:
        model = Product
        fields = ["productId", "brand", "name", "root_category", 
                  "main_category", "sub_category","description", "thumbnail", 
                  "availability","weight", "launch_date"]

class ProductDetailsRetriveSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True)
    variations = VariationsSerializer(many=True)
    root_category = RootViewSerializer()
    main_category = MainViewSerializer()
    sub_category = SubViewSerializer()
    details = PDetailsSerializer()
    images = ProductImageSerializer(many=True)
    class Meta:
        model = Product
        fields = "__all__"



class UnitCreateSerializer(serializers.ModelSerializer):
    unit_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Unit
        fields = ["unit_id","color_code", "variant", "stock", "selling_price", "offer_price", "original_price", "product"]

    def create(self, validated_data):
        u_id = uuid.uuid1()
        unit = Unit.objects.create(unit_id = u_id, **validated_data)
        return unit


class UnitRetriveSerializer(serializers.ModelSerializer):
    color_code = ColorSerializer()
    variant = VariationsSerializer()
    product = ProductRetriveSerializer()
    class Meta:
        model = Unit
        fields = "__all__"

class UnitDetailsRetriveSerializer(serializers.ModelSerializer):
    color_code = ColorSerializer()
    variant = VariationsSerializer()
    product = ProductDetailsRetriveSerializer()
    class Meta:
        model = Unit
        fields = "__all__"


