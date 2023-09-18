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
    path('get-order-price/<uuid:order_id>/', OrderItemsConfirmationView.as_view(), name='get-price'),
    path('cancel-order/<uuid:order_id>/', CancelOrderView.as_view(), name='cancel-order'),
    path('retrive/<uuid:order_id>/', OrderDetailsRetriveView.as_view(), name='order-retrive'),

    path('get-seller-orders/', SellerOrderListView.as_view(), name='seller-order-list'),
    path('order-accept-or-reject/', OrderAcceptOrReject.as_view(), name="accept-or-reject"),

    path('get-customer-orders/', CustomerOrderListView.as_view(), name='customer-order-list'),
    path('delete/<uuid:order_id>/', CustomerOrderCancelView.as_view(), name='delete-order'),
    path('initiate-return/<uuid:order_id>/', OrderReturnInitiationView.as_view(), name='initiate-return'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)