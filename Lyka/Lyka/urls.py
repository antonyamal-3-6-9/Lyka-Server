from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("product/", include("lyka_products.urls")),
    path('category/', include("lyka_categories.urls")),
    path('seller/', include("lyka_seller.urls")),
    path("customer/", include("lyka_customer.urls")),
    path("payments/", include("lyka_payment.urls")),
    path("address/", include("lyka_address.urls")),
    path("cart/", include("lyka_cart.urls")),
    path('order/', include("lyka_order.urls")),
    path('admin/', include("lyka_admin.urls"))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
