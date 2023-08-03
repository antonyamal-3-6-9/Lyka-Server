from django.db import models
from lyka_user.models import LykaUser
from lyka_payment.models import Wallet
from lyka_address.models import SellerStoreAddress
import uuid


class SellerOtp(models.Model):
    otp = models.CharField(max_length=9, null=True)
    verification_credential = models.CharField(max_length=255, null=True, unique=True)

class AddressProof(models.Model):
    address_proof_number = models.CharField(max_length=200, null=True, blank=True)
    address_proof_name = models.CharField(max_length=200, null=True, blank=True)
    address_proff_dob = models.CharField(max_length=200, null=True, blank=True)
    address_proof_type = models.CharField(max_length=200, null=True, blank=True)


class PanCard(models.Model):
    pan_number = models.CharField(max_length=50)


class BankAccount(models.Model):
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50)
    bank_branch = models.CharField(max_length=50)
    bank_ifsc = models.CharField(max_length=50)


class GstRegistrationNumber(models.Model):
    gst_number = models.CharField(max_length=50)


class Seller(models.Model):
    user = models.OneToOneField(LykaUser, on_delete=models.CASCADE)
    unique_id = models.UUIDField(primary_key=True)
    bussiness_name = models.CharField(max_length=50)

    verified = models.BooleanField(default=False)
    number_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    address_verified = models.BooleanField(default=False)
    pan_verified = models.BooleanField(default=False)
    bank_account_verified = models.BooleanField(default=False)
    gstin_verified = models.BooleanField(default=False)


    address_proof = models.OneToOneField(AddressProof, on_delete=models.SET_NULL, null=True)
    pan_card = models.OneToOneField(PanCard, on_delete=models.SET_NULL, null=True)
    bank_account = models.OneToOneField(BankAccount, on_delete=models.SET_NULL, null=True)
    gstin = models.OneToOneField(GstRegistrationNumber, on_delete=models.SET_NULL, null=True)

    wallet = models.OneToOneField('lyka_payment.Wallet', on_delete=models.CASCADE, null=True)

    def is_verified(self):
        if self.address_verified and self.pan_verified and self.bank_account_verified and self.gstin_verified:
            self.verified = True
        return self.verified
    

class PickupStore(models.Model):
    store_name = models.CharField(max_length=50)
    store_id = models.UUIDField(primary_key=True)
    store_address = models.OneToOneField('lyka_address.SellerStoreAddress', on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='store_owner', null=True)






