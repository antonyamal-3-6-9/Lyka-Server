from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
import random
import string

# Create your models here.

def numberGenerator():
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for _ in range(5))
    return unique_id



class LykaUserManager(BaseUserManager):
    def create_user(self, email, role, password=None, phone=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not role:
            raise ValueError('The Role field must be set')
        

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, role=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email=email, role=role, password=password,**extra_fields)
    
    def get(self, **kwargs):
        try:
            user = self.get_queryset().get(**kwargs)
            return user
        except self.model.DoesNotExist:
            return None
        
    def role_exists_email(self, email=None, role=None):
        try:
            self.get_queryset().get(email=email, role=role)
            return True
        except ObjectDoesNotExist:
            return False
        
    def role_exists_phone(self, phone=None, role=None):
        try:
            self.get_queryset().get(phone=phone, role=role)
            return True
        except ObjectDoesNotExist:
            return False

class LykaUser(AbstractBaseUser, PermissionsMixin):
    CUSTOMER = 'customer'
    SELLER = 'seller'
    ADMIN = 'ADMIN'
    USER_ROLES = [
        (CUSTOMER, 'Customer'),
        (SELLER, 'Seller'),
        (ADMIN, 'Admin')
    ]

    email = models.EmailField(max_length=60)
    phone = models.CharField(max_length=10, null=True)
    is_customer = models.BooleanField(null=True)
    is_seller = models.BooleanField(null=True)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    otp = models.CharField(max_length=9, blank=True, null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def has_module_perms(self, app_label):
        return self.is_active and self.is_staff

    objects=LykaUserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']



class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)


class UserCreationAuth(models.Model):
    CUSTOMER = 'customer'
    SELLER = 'seller'
    ADMIN = 'ADMIN'
    USER_ROLES = [
        (CUSTOMER, 'Customer'),
        (SELLER, 'Seller'),
        (ADMIN, 'Admin')
    ]
    email = models.CharField(max_length=50)
    token = models.CharField(max_length=250)
    role = models.CharField(max_length=50, choices=USER_ROLES)



class Notification(models.Model):
    owner = models.ForeignKey(LykaUser, on_delete=models.CASCADE)
    message = models.TextField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)