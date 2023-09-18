from rest_framework import serializers
from .models import *
from django.conf import settings
from rest_framework.exceptions import ValidationError
import requests



class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = ['name', 'street_one', 'street_two', 'city', 'state', 'country', 'phone', 'landmark', 'alternate_phone', 'zip_code', 'address_type']

    def is_valid_pincode(self, pincode):
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        response = requests.get(url)
        data = response.json()
        print(data[0]['Status'])
        if data[0]["Status"] == "Success":
            return True

    def create(self, validated_data):
        zip_code = validated_data["zip_code"]
        if self.is_valid_pincode(zip_code):
            return super().create(validated_data)
        else:
            raise ValidationError("Addres is invalid")
        

class SellerStoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerStoreAddress
        fields = "__all__"

    def is_valid_pincode(self, pincode):
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        response = requests.get(url)
        data = response.json()
        if data["Status"] == "Success":
            return True

    def create(self, validated_data):
        zip_code = validated_data["zip_code"]
        if self.is_valid_pincode(zip_code):
            return super().create(validated_data)
        else:
            raise ValidationError("Addres is invalid")

class SellerStoreAddressRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerStoreAddress
        fields = "__all__" 

class SellerStoreAddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerStoreAddress
        fields = "__all__"   

        
         

class CustomerAddressRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"