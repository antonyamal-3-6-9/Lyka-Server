from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path("register/", CustomerCreateView.as_view(), name="customer-create"),
    path('is-loggedin/', IsCustomerLoggedInOrNot.as_view(), name="is-logged-in"),
    path('customer-exists-or-not/<int:phone_number>/', CustomerExistsOrNot.as_view(), name="customer-exists"),
    path('otp-login-create/<int:phone>/', PhoneOtpLogin.as_view(), name="otp-create"),
    path('otp-login-verify/', PhoneOtpLogin.as_view(), name='otp-verify'),
    path('login-using-phone/', PhoneLogin.as_view(), name='phone-login'),
    path('login-using-email/', EmailLogin.as_view(), name="email-login"),
    path('logout/', CustomerLogOutView.as_view(), name='logout'),
    path('update/<int:pk>/', CustomerUserUpdateView.as_view(), name='customer-update'),
    path('retrive/', CustomerProfileRetriveView.as_view(), name='retrive-profile'),
    path('otp-create/<int:phone>/', CustomerOtpView.as_view(), name='otp-create-'),
    path('otp-verify/', CustomerOtpView.as_view(), name="otp-verify-"),
    path('create-email-otp/<str:to_email>/', EmailOtpVerificationView.as_view(), name='otp-email-create'),
    path('verify-email-otp/', EmailOtpVerificationView.as_view(), name='verify-otp-email'),
    path('has-password/', IsPasswordExistsView.as_view(), name='has-password'),
    path('set-password/', PasswordChangeView.as_view(), name='change-password')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)