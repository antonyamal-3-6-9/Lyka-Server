from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path("lyka-admin/root/add/", RootAddView.as_view(), name='root-add'),
    path("lyka-admin/main/add/", MainAddView.as_view(), name="main-add"),
    path("lyka-admin/sub/add/", SubAddView.as_view(), name="sub-add"),

    path('root/', RootView.as_view(), name='root'),
    path('main/', MainView.as_view(), name="main"),
    path('sub/', SubView.as_view(), name="sub"),
    path('lyka-admin/list/all/', CategoryListView.as_view(), name='list-all'),

    path('lyka-admin/root/delete/<uuid:root_id>/', RootDelete.as_view(), name='root-delete'),
    path('lyka-admin/main/delete/<uuid:main_id>/', MainDelete.as_view(), name="main-delete"),
    path("lyka-admin/sub/delete/<uuid:sub_id>/", SubDelete.as_view(), name="sub-delete"),

    path("lyka-admin/root/update/", RootUpdateView.as_view(), name='root-update'),
    path('lyka-admin/main/update/', MainUpdateView.as_view(), name='main-delete'),
    path('lyka-admin/sub/update/', SubUpdateView.as_view(), name='sub-update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
