from rest_framework import serializers
from .models import Notification, LykaUser


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['message', 'time']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LykaUser
        fields = ["first_name", "last_name", "role", "email_id"]