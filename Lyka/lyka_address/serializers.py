from rest_framework import serializers
from .models import *
from django.conf import settings



class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = ['name', 'street_one', 'street_two', 'city', 'state', 'country', 'phone', 'alternate_phone', 'zip_code', 'address_type']
        

class SellerStoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerStoreAddress
        fields = "__all__"

class CustomerAddressRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"