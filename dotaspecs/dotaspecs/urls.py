from django.conf.urls.static import static
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from django.views.decorators.cache import cache_page
from django.views.static import serve as mediaserve
from django.urls import re_path

from dotaspecs import settings
from specs.views import *

from specs import views

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='home'),
    path('', include('specs.urls')),
    path('', include('allauth.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('pages/', include('django.contrib.flatpages.urls')),
]

if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve, {'document_root': settings.MEDIA_ROOT})
    ]

handler403 = 'specs.system.views.tr_handler403'
handler404 = 'specs.system.views.tr_handler404'
handler500 = 'specs.system.views.tr_handler500'
