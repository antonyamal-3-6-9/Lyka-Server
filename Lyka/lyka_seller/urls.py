from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *




urlpatterns = [
    path("register/", SellerCreateView.as_view(), name='seller-create'),
    path("password-login/", PasswordLoginView.as_view(), name='seller-login-email'),
    path("pan-verify/", SellerPanVerificationView.as_view(), name='seller-pan-verify'),
    path("address-verify/", SellerAddressVerificationView.as_view(), name='seller-address-verify'),
    path("bank-verify/", SellerBankVerificationView.as_view(), name='seller-bank-verify'),
    path("gst-verify/", SellerGstVerificationView.as_view(), name='seller-gst-verify'),
    path("otp-login-create/<str:to_email>/", OtpLoginView.as_view(), name='otp-create'),
    path("otp-login-verify/", OtpLoginView.as_view(), name="otp-verify"),
    path("email-otp-create/<str:to_email>/", EmailOtpVerificationView.as_view(), name='email-otp-create'),
    path("email-otp-verify/", EmailOtpVerificationView.as_view(), name="email-otp-verify"),
    path("seller-exists-or-not/", SellerExistsOrNot.as_view(), name='seller-exist-or-not'),
    path("seller-loggedin-or-not/", SellerLoggedInOrNot.as_view(), name='loggedin-or-not'),
    path("get-seller/", SellerRetriveView.as_view(), name="get-seller"),
    path("add-store/", AddPickUpStoreView.as_view(), name='add-store'),
    path("get-store/", PickupStoreRetirveView.as_view(), name='get-store'),
    path('delete-store/<uuid:pk>/', PickUpStoreDeleteView.as_view(), name='store-delete'),
    path("verified-or-not/", SellerVerifiedOrNOt.as_view(), name="seller-verified"),
    path("get-seller-profile/", GetSellerView.as_view(), name='get-seller-profile'),
    path("update-profile/<uuid:pk>/", UpdateSellerProfile.as_view(), name='update-profile'),
    path("change-password/", SellerPasswordChangeView.as_view(), name='password-change'),
    path("logout/", SellerLogOutView.as_view(), name='logout'),
    path('store-exists-or-not/', IsStoreExistsOrNot.as_view(), name="store-exists"),
    path('get-business-name/', SellerBusinessNameFetchView.as_view(), name='get-business')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)