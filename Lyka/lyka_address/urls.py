from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path("get-address/<int:address_id>/", StoreAddressRetriveView.as_view(), name='get-address'),
    path("put-address/<int:pk>/", StoreAddressEditView.as_view(), name='put-address'),
    path("create-customer-address/", CustomerAddressCreateView.as_view(), name='add-customer-address'),
    path("get-customer-address/", CustomerAddressListView.as_view(), name='get-customer-address'),
    path("get-customer-address/<int:address_id>/", CustomerAddressRetriveView.as_view(), name="get-customer-address-id"),
    path("put-customer-address/<int:pk>/", CustomerAddressEditView.as_view(), name='put-customer-address')
] 



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
