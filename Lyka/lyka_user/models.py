from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class LykaUserManager(BaseUserManager):
    def create_user(self, phone, role, password=None, email=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone Number field must be set')
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

    def create_superuser(self, phone, password=None, role=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone=phone, role=role, password=password,**extra_fields)
    
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

    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=10)
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


    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['role']
