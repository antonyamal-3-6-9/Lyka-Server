from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('add-to-cart/', AddtoCartView.as_view(), name='add-to-cart'),
    path('get-cart-item/', RetriveCartView.as_view(), name='get-cart'),
    path('item-in-cart/<uuid:unit_id>/', ItemInCartOrNotView.as_view(), name='in-cart'),
    path('increment-cart/<int:cart_item_id>/', IncrementCartView.as_view(), name='increase-cart'),
    path('decrement-cart/<int:cart_item_id>/', DecrementCartView.as_view(), name='decrease-cart'),
    path('delete-cart-item/<int:cart_item_id>/', DeleteCartItemView.as_view(), name='delete-cart'),
    path('cart-exists-or-not/', IsCartExistsOrNot.as_view(), name='cart-exists')
] 



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)