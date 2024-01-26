from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path("create-product/", ProductCreateView.as_view(), name='create'),
    path('check-product/', ProductCheckView.as_view(), name='check'),
    path("create-item/", LykaUnitCreateView.as_view(), name='create-item'),
    path("get-details/", ShowDetailsView.as_view(), name='get-details'),
    path("put-details/", ProductDetailsAddView.as_view(), name="put-details"),
    path('<uuid:product_id>/images/', ImageUploadView.as_view(), name='image-upload'),
    path('get-seller-item/', ItemSellerListView.as_view(), name='seller-products'),
    path('make-live/', ItemMakeLiveView.as_view(), name='make-live'),
    path('get-seller-item-details/', ItemRetriveView.as_view(), name='get-product-details'),
    path('delete-item/<uuid:unit_id>/', ItemVariantDeleteView.as_view(), name="delete-product"),
    path('add-more-stock/', ItemAddMoreStockView.as_view(), name='add-more-stock'),
    path('get-all-items/', UnitListView.as_view(), name='product-retrive-serializer'),
    path('get-item-details/<uuid:unit_id>/', ItemRetriveView.as_view(), name="get-product-details"),
    path('get-product-variations/<uuid:pk>/', ProductVariationGetView.as_view(), name='get-variations'),
    path('get-items/main/<uuid:main>/', LykaItemMainCategoryRetriveView.as_view(), name='get-main-items'),
    path('get-items/root/<uuid:root>/', LykaItemRootCategoryRetriveView.as_view(), name="get-root-items"),
    path('get-items/sub/<uuid:sub>/', LykaItemSubCategoryRetriveView.as_view(), name="get-sub-items"),
    path('color-or-variation-exists/<uuid:seller_id>/<uuid:product_id>/<int:color_id>/<int:variant_id>/<str:is_variant_color>/', ColorOrVariantExistsView.as_view(), name='color-exists' ),
    path('lyka-admin/list/all/', ProductsListView.as_view(), name='product-list'),

    path('lyka-admin/delete/<uuid:product_id>/', ProductDeleteView.as_view(), name="product-delete"),

    path('lyka-admin/color/add/', ColorAddView.as_view(), name='add-color'),
    path('lyka-admin/variant/add/', VariantAddView.as_view(), name='add-variant'),
    path('lyka-admin/variant/remove/', VariantDeleteView.as_view(), name='delete-variant'),
    path('lyka-admin/color/remove/', ColorDeleteView.as_view(), name="color-delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)