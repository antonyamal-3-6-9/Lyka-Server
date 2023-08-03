from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *




urlpatterns = [
    path("register/", SellerCreateView.as_view(), name='seller-create'),
    path("login-phone/", PhoneLoginView.as_view(), name='seller-login-phone'),
    path("login-email/", EmailLoginView.as_view(), name='seller-login-email'),
    path("pan-verify/", SellerPanVerificationView.as_view(), name='seller-pan-verify'),
    path("address-verify/", SellerAddressVerificationView.as_view(), name='seller-address-verify'),
    path("bank-verify/", SellerBankVerificationView.as_view(), name='seller-bank-verify'),
    path("gst-verify/", SellerGstVerificationView.as_view(), name='seller-gst-verify'),
    path("phone-otp-create/", PhoneOtpVerificationView.as_view(), name='phone-otp-create'),
    path("phone-otp-verify/", PhoneOtpVerificationView.as_view(), name="phone-otp-verify"),
    path("email-otp-create/", EmailOtpVerificationView.as_view(), name='email-otp-create'),
    path("email-otp-verify/", EmailOtpVerificationView.as_view(), name="email-otp-verify"),
    path("phone-otp-login-create/", PhoneOtpLogin.as_view(), name='phone-login-otp-create'),
    path("phone-otp-login-verify/", PhoneOtpLogin.as_view(), name="phone-otp-login-verify"),
    path("seller-exists-or-not/", SellerExistsOrNot.as_view(), name='seller-exist-or-not'),
    path("seller-loggedin-or-not/", SellerLoggedInOrNot.as_view(), name='loggedin-or-not'),
    path("get-seller/", SellerRetriveView.as_view(), name="get-seller"),
    path("add-store/", AddPickUpStoreView.as_view(), name='add-store'),
    path("get-store/", PickupStoreRetirveView.as_view(), name='get-store'),
    path('delete-store/<uuid:pk>/', PickUpStoreDeleteView.as_view(), name='store-delete'),
    path("verified-or-not/", SellerVerifiedOrNOt.as_view(), name="seller-verified"),
    path("get-seller-profile/", GetSellerView.as_view(), name='get-seller-profile'),
    path("update-profile/<uuid:pk>/", UpdateSellerProfile.as_view(), name='update-profile'),
    path("change-password/", SellerPasswordChangeView.as_view(), name='password-change')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)