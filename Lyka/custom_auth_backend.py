from django.contrib.auth.backends import ModelBackend
from lyka_customer.models import LykaUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, password=None, phone=None, role=None, **kwargs):
        try:
            user = LykaUser.objects.get(phone=phone, role=role)
        except LykaUser.DoesNotExist:
            return None


        if user is not None and user.check_password(password):
            return user
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return LykaUser.objects.get(pk=user_id)
        except LykaUser.DoesNotExist:
            return None
