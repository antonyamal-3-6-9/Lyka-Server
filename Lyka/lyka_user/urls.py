from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import NotificationView

urlpatterns = [
    path("notifications/", NotificationView.as_view(), name='noti-view')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)