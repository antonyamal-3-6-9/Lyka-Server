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
    path('login-using-email/', EmailLogin.as_view(), name="email-login")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)