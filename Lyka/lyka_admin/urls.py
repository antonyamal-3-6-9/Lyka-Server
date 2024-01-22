from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('commission/retrieve/', CommissionRetrieveView.as_view(), name="commission_retrieve"),
    path('commissions/days/', CommissionDaysView.as_view(), name='commission_days'),
    path('commissions/weeks/', CommissionWeeksView.as_view(), name="commission_weeks"),
    path('commissions/months/', CommissionMonthsView.as_view(), name='commissions_month'),
    path('commissions/years/', CommissionYearsView.as_view(), name='commission_years'),
    path('commission/report/', CommissionReportRetrieveView.as_view(), name='commission_report'),
    path('commission/report/timeline/', CommissionReportTimelineView.as_view(), name='commission_report_timeline'),

    path('login/', AdminLoginView.as_view(), name="admin-login"),
    path('logout/', AdminLogoutView.as_view(), name='admin-logout'),

    path('product/verify/<uuid:product_id>/<str:verification_status>/', ProductVerificationView.as_view(), name='product-verify'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


