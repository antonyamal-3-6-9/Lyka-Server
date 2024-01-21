from rest_framework import serializers
from .models import *
from lyka_address.serializers import SellerStoreAddressRetriveSerializer
import uuid
from rest_framework.exceptions import ValidationError
from lyka_customer.models import LykaUser
from django.core.exceptions import ObjectDoesNotExist


class SellerUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = LykaUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'role']

    def create(self, validated_data):
        email = validated_data.pop('email')
        phone = validated_data.pop('phone')

        try:
            if LykaUser.objects.role_exists_email(email=email, role=LykaUser.SELLER):
                raise ValidationError({"error": "User exists with the given email."})
            if LykaUser.objects.role_exists_phone(phone=phone, role=LykaUser.SELLER):
                raise ValidationError({"error": "User exists with the given phone."})
            else:
                user = LykaUser.objects.create_user(email=email, phone=phone, role=LykaUser.SELLER, **validated_data)
                user.save()
                return user
        except ObjectDoesNotExist:
            raise ValidationError({"error": "An error occurred during seller creation."})


        
class AddressProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressProof
        fields = "__all__"

    def create(self, validated_data):
        address_proof_number = validated_data.get('address_proof_number')
        if AddressProof.objects.filter(address_proof_number=address_proof_number).exists():
            raise serializers.ValidationError("Address Proof number already exists.")
        return super().create(validated_data)


class PanCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanCard
        fields = "__all__"

    def create(self, validated_data):
        pan_number = validated_data.get('pan_number')
        if PanCard.objects.filter(pan_number=pan_number).exists():
            raise serializers.ValidationError("PAN number already exists.")
        return super().create(validated_data)


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"

    def create(self, validated_data):
        account_number = validated_data.get('account_number')
        if BankAccount.objects.filter(account_number=account_number).exists():
            raise serializers.ValidationError("Account number already exists.")
        return super().create(validated_data)


class GstRegistrationNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GstRegistrationNumber
        fields = "__all__"

    def create(self, validated_data):
        gst_number = validated_data.get('gst_number')
        if GstRegistrationNumber.objects.filter(gst_number=gst_number).exists():
            raise serializers.ValidationError("GST number already exists.")
        return super().create(validated_data)



class SellerCreationSerializer(serializers.ModelSerializer):
    user = SellerUserSerializer()

    class Meta:
        model = Seller
        fields = ['user', 'bussiness_name']

    def create(self, validated_data):
        seller_id = uuid.uuid1()
        user_data = validated_data.pop('user')
        user_serializer = SellerUserSerializer(data=user_data)

        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        seller = Seller.objects.create(user=user, unique_id=seller_id, **validated_data)
        seller.email_verified = True
        seller.number_verified = True
        seller.save()
        return seller


class PickupStoreSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = PickupStore
        fields = ["store_name", "store_id"]
    
    def create(self, validated_data):
        s_id = uuid.uuid1()
        store = PickupStore.objects.create(store_id = s_id, **validated_data)
        return store
    

class PickupStoreViewSerializer(serializers.ModelSerializer):
    store_address = SellerStoreAddressRetriveSerializer()
    class Meta:
        model = PickupStore
        fields = "__all__"

class SellerUserGetSerializer(serializers.ModelSerializer):
    user = SellerUserSerializer()
    class Meta:
        model = Seller
        fields = ["user"]


class SellerVerifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["verified", "number_verified", "email_verified", "address_verified", 
                  "pan_verified", "gstin_verified", "bank_account_verified"]
        

class SellerGetSerializer(serializers.ModelSerializer):
    user = SellerUserSerializer()
    class Meta:
        model = Seller
        fields = ["user", "unique_id", "bussiness_name", "verified", "number_verified",
                   "email_verified", "address_verified", "pan_verified", "gstin_verified", 
                   "bank_account_verified" ]

class SellerUserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    class Meta:
        model = LykaUser
        fields = ["first_name", "last_name", "email", "phone"]     

class SellerUpdateSerializer(serializers.ModelSerializer):
    bussiness_name = serializers.CharField(required=False)
    user = SellerUserUpdateSerializer()
    class Meta:
        model = Seller
        fields = ["user", "bussiness_name"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})       
        if user_data:
            if "email" in user_data:
                if LykaUser.objects.role_exists_email(email=user_data["email"], role=LykaUser.SELLER):
                    raise ValidationError("Customer already exists with the same email")
            elif "phone" in user_data:
                if LykaUser.objects.role_exists_phone(phone=user_data["phone"], role=LykaUser.SELLER):
                    raise ValidationError("Customer exists with the given phone")
        user_serializer = SellerUserUpdateSerializer(instance.user, user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        if user.phone is not None:
            instance.number_verified = True
            instance.save()
        if "bussiness_name" in validated_data:
            if Seller.objects.filter(bussiness_name=bussiness_name).exists():
                raise ValidationError("Business name already exists")
            instance.bussiness_name = bussiness_name
            instance.save()
        return super().update(instance, validated_data)
    

class SellerBusinessNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["bussiness_name"]

class SellerStoreNameRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupStore
        fields = ['store_name']




