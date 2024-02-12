from rest_framework import serializers
from .models import *
import string
import secrets

class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = "__all__"


class TotalCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Total_Commission
        fields = "__all__"

