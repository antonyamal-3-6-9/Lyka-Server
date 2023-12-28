from rest_framework import serializers
from .models import *
from django.conf import settings
from rest_framework.exceptions import ValidationError
import requests


def is_valid_city(city, district):
    city_url = f"https://api.postalpincode.in/pincode/{city}"
    city_response = requests.get(city_url)
    city_data = city_response.json()
    if city_data["Status"] == "Success":
        if city_data[0]["PostOffice"][0]["District"] == district:
            return "Success"
        else:
            return "district-error"
    else:
        return "city-error"

def is_valid_pincode(pincode, city, district):
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    response = requests.get(url)
    data = response.json()
    status = data[0]['Status']

    if status == "Success":
        if data[0]["PostOffice"][0]["District"] == district:
            if data[0]["PostOffice"][0]["Block"] == city:
                return "success"
            else:
                return "city-error"
        else:
            return "district-error"
    else:
        return "code-error"
    

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = ['name', 'street_one', 'street_two', 'city', 'state', 'country', 'phone', 'landmark', 'alternate_phone', 'zip_code', 'address_type']

    def create(self, validated_data):
        zip_code = validated_data["zip_code"]
        city = validated_data["city"]
        district = validated_data["district"]
        validation_response = is_valid_pincode(pincode=zip_code, city=city, district=district)
        if validation_response  == "success":
            return super().create(validated_data)
        elif validation_response == "city-error":
            raise ValidationError("Enter a valid City")
        elif validation_response == "district-error":
            raise ValidationError("Enter a valid District")
        elif validation_response == "code-error":
            raise ValidationError("Enter a valid Pincode")
        

class SellerStoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerStoreAddress
        fields = "__all__"

    def create(self, validated_data):
        zip_code = validated_data["zip_code"]
        city = validated_data["city"]
        district = validated_data["district"]
        validation_response = is_valid_pincode(pincode=zip_code, city=city, district=district)
        if validation_response  == "success":
            return super().create(validated_data)
        elif validation_response == "city-error":
            raise ValidationError("Enter a valid City")
        elif validation_response == "district-error":
            raise ValidationError("Enter a valid District")
        elif validation_response == "code-error":
            raise ValidationError("Enter a valid Pincode")
        

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

class CustomerAddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"