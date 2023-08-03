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
        fields = ['phone','role']

    def create(self, validated_data):
        try:
            phone = validated_data.pop('phone')
            if LykaUser.objects.role_exists_phone(phone=phone, role=LykaUser.CUSTOMER):
                raise ValidationError("Customer already exists with same number")
            user = LykaUser.objects.create_user(phone=phone, role=LykaUser.CUSTOMER)
            return user
        except ObjectDoesNotExist:
            raise ValidationError("An error occured during the Customer Creation")

class CustomerCreateSerializer(serializers.ModelSerializer):
    user = CustomerUserSerializer()
    class Meta:
        model = Customer
        fields = ['user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = CustomerUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        customer = Customer.objects.create(user=user)
        return customer

class CustomerUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LykaUser
        fields = ['first_name', 'last_name', 'email']

    def create(self, validated_data):
        user = self.context['request'].user
        email = validated_data.get('email')

        if email and LykaUser.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise ValidationError({'email': 'Customer with this email already exists.'})

        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        return user
    

class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = "__all__"



    

