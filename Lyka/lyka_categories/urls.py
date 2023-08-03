from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path("root-add/", RootAddView.as_view(), name='root-add'),
    path("main-add/", MainAddView.as_view(), name="main-add"),
    path("sub-add/", SubAddView.as_view(), name="sub-add"),
    path('root/', RootView.as_view(), name='root'),
    path('main/', MainView.as_view(), name="main"),
    path('sub/', SubView.as_view(), name="sub")

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
