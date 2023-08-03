from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('create-single-order/', DirectOrderCreateView.as_view(), name='single-order-creation'),
    path('create-multiple-order/', CartCreateOrderView.as_view(), name='multiple-order-creation'),
    path('get-order/<uuid:order_id>/', OrderRetriveView.as_view(), name='get-order'),
    path('increament-item/<uuid:order_id>/', OrderItemIncrementView.as_view(), name='increase-order'),
    path('decreament-item/<uuid:order_id>/', OrderItemDecrementView.as_view(), name='decrease-order'),
    path('confirm-items/<uuid:order_id>/', OrderItemsConfirmationView.as_view(), name='confirm-items'),
    path('add-address/<uuid:order_id>/<int:address_id>/', OrderAddressUpdateView.as_view(), name='add-address'),
    path('apply-coupon/', OrderApplyCoupon.as_view(), name='order-apply-coupon'),
    path('get-order-price/<uuid:order_id>/', OrderItemsConfirmationView.as_view(), name='get-price')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)