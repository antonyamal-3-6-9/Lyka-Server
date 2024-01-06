from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path("auth/<str:email>/", CustomerRequestView.as_view(), name="create-link"),
    path("auth/verify-link/", CustomerRequestView.as_view(), name="verify-link"),
    path("create/", CustomerCreateView.as_view(), name="customer-verify"),
    path('is-loggedin/', IsCustomerLoggedInOrNot.as_view(), name="is-logged-in"),
    path('customer-exists-or-not/<int:phone_number>/', CustomerExistsOrNot.as_view(), name="customer-exists"),
    path('password-login/', PasswordLoginView.as_view(), name="password-login"),
    path('otp-login-create/<str:email>/', OtpLoginView.as_view(), name="otp-login-create"),
    path('otp-login-verify/', OtpLoginView.as_view(), name='otp-login-verify'),
    path('logout/', CustomerLogOutView.as_view(), name='logout'),
    path('update/<int:pk>/', CustomerUserUpdateView.as_view(), name='customer-update'),
    path('retrive/', CustomerProfileRetriveView.as_view(), name='retrive-profile'),
    path('create-email-otp/<str:to_email>/', EmailOtpVerificationView.as_view(), name='otp-email-create'),
    path('verify-email-otp/', EmailOtpVerificationView.as_view(), name='verify-otp-email'),
    path('has-password/', IsPasswordExistsView.as_view(), name='has-password'),
    path('set-password/', PasswordChangeView.as_view(), name='change-password')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)