from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path("razorpay-create/", RazorPayOrderPaymentCreationView.as_view(), name='create'),
    path("razorpay-capture/", RazorPayOrderPaymentCaptureView.as_view(), name='capture'),
    

    path('get-coupons/', CouponRetriveView.as_view(), name='get-coupon'),

    path('create-paypal-order/', PaypalPaymentView.as_view(), name="paypal-create"),
    path('capture-paypal-order/<str:paypal_order_id>/<uuid:lyka_order_id>/', PaypalPaymentView.as_view(), name='capture-paypal'),

    path('create-stripe-order/', StripePaymentView.as_view(), name='stripe-create'),
    path('capture-stripe-order/', StripePaymentView.as_view(), name='capture-stripe'),
]








if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)