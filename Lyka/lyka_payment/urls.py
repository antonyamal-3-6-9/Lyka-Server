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

    path('seller/get-sales/day/', SalesDaysRetriveView.as_view(), name='get-sales'),
    path('seller/get-sales/week/', SalesWeekView.as_view(), name='sales-week'),
    path('seller/get-sales/month/', SalesMonthView.as_view(), name='sales-month'),
    path('seller/get-sales/year/', SalesYearView.as_view(), name='sales-year'),

    path('seller/get-sales-report/', SalesReportRetriveView.as_view(), name='get-sales-report'),
    path('seller/get-sales-report/time-line/', SalesReportTimelimeView.as_view(), name='get-sales-report-timeline'),

    path('seller/get-sales/', SalesRetriveView.as_view(), name='get-sales'),

    path('lyka-admin/coupon/create/', CouponGenerateView.as_view(), name="coupon-create"),
    path('lyka-admin/coupon/update/<int:pk>/', CouponUpdateView.as_view(), name='coupon-update'),
    path('lyka-admin/coupon/delete/<int:pk>/', CouponDeleteView.as_view(), name="coupon-delete"),
    path('lyka-admin/coupon/list/', CouponListVIew.as_view(), name='coupon-list'),

    path('lyka-admin/charge/create/', TaxCreateView.as_view(), name="create-tax"),
    path('lyka-admin/charge/update/<int:pk>/', TaxUpdateView.as_view(), name='update-tax'),
    path('lyka-admin/charge/delete/<int:pk>/', TaxDeleteView.as_view(), name='delete-tax'),
    path('lyka-admin/charge/list/', TaxListView.as_view(), name="list-tax"),

    path('lyka-admin/coupon/toggle/<int:pk>/', CouponToggleActivationView.as_view(), name="coupon-toggle"),
    path('lyka-admin/charge/toggle/<int:pk>/', TaxToggleActivationView.as_view(), name='toggle-tax'),
]








if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)