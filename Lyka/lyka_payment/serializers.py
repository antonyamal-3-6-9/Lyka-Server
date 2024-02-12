from rest_framework import serializers
from .models import *
from lyka_order.models import Tax
import uuid


class WalletSerializer(serializers.ModelSerializer):
    wallet_id = serializers.UUIDField(read_only = True)
    class Meta:
        model = Wallet
        fields = ["wallet_id"]

    def create(self):
        w_id = uuid.uuid1()
        wallet = Wallet.objects.create(wallet_id = w_id)
        return wallet

  
class TransactionSerializer(serializers.ModelSerializer):
    ref_no = serializers.UUIDField(read_only = True)
    class Meta:
        model = OrderTransaction
        fields = "__all__"

    def create(self, validated_data):
        r_no = uuid.uuid1()
        transaction = OrderTransaction.objects.create(ref_no=r_no, **validated_data)
        return transaction


class CouponSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = CouponType
        fields = "__all__"

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)


class TransactionRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTransaction
        fields = "__all__"


class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = "__all__"

class TaxSerializer(serializers.ModelSerializer):
    added_at = serializers.DateTimeField(read_only=True)
    active = serializers.BooleanField(read_only=True)
    class Meta:
        model = Tax
        fields = "__all__"