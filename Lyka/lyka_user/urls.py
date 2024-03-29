from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path("notification/", NotificationView.as_view(), name='noti-view'),
    path("active/", CheckActiveView.as_view(), name="check-active"),
    path('lyka-admin/list/all/', UserListView.as_view(), name='user-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)