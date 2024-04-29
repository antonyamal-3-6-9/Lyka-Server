from rest_framework import serializers
from .models import *
from lyka_cart.serializers import Cartserializer
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import uuid

class CustomerUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    class Meta:
        model = LykaUser
        fields = ['email','role']

    def create(self, validated_data):
        try:
            email = validated_data.pop('email')
            if LykaUser.objects.role_exists_phone(phone=email, role=LykaUser.CUSTOMER):
                raise ValidationError("Customer already exists with same number")
            user = LykaUser.objects.create_user(phone=email, role=LykaUser.CUSTOMER)
            return user
        except ObjectDoesNotExist:
            raise ValidationError("An error occured during the Customer Creation")


class CustomerCreateSerializer(serializers.ModelSerializer):
    user = CustomerUserSerializer()
    class Meta:
        model = Customer
        fields = ['user']

    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            user_serializer = CustomerUserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            customer = Customer.objects.create(user=user)
            return customer
        except ObjectDoesNotExist:
            raise ValidationError("Try Again Later")


class CustomerUserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    class Meta:
        model = LykaUser
        fields = ['first_name', 'last_name', 'email', 'phone']



class CustomerUpdateSerializer(serializers.ModelSerializer):
    user = CustomerUserUpdateSerializer()

    class Meta:
        model = Customer
        fields = ["user"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        
        if user_data:
            if "email" in user_data:
                if LykaUser.objects.role_exists_email(email=user_data["email"], role=LykaUser.CUSTOMER):
                    raise ValidationError("Customer already exists with the same email")
            elif "phone" in user_data:
                if LykaUser.objects.role_exists_phone(phone=user_data["phone"], role=LykaUser.CUSTOMER):
                    raise ValidationError("Customer exists with the given phone")
            
            user_serializer = CustomerUserUpdateSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            
            if "email" in user_data:
                instance.is_email_verified = False
            if user.phone is not None:
                instance.is_verified = True

        instance = super().update(instance, validated_data)
        instance.save()
        return instance



class CustomerReviewSerializer(serializers.ModelSerializer):
    added_on = serializers.DateTimeField(read_only=True)
    class Meta:
        model = CustomerReview
        fields = "__all__"

class CustomerUserRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LykaUser
        fields = ["first_name", "last_name", "phone", "email", 'role']

class CustomerRetriveSerializer(serializers.ModelSerializer):
    user = CustomerUserRetriveSerializer()
    class Meta:
        model = Customer
        fields = ["user", "id", "is_email_verified", "is_verified"]

