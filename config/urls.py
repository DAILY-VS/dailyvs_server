from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from django.urls import re_path as url

urlpatterns = [
    path("2F650631682090A674BBB3CDBD3A080381C2E37B4B58DB40878FE5AD94635D4E/admin/", admin.site.urls), 
    path("2F650631682090A674BBB3CDBD3A080381C2E37B4B58DB40878FE5AD94635D4E/", include("vote.urls")), #vote app
    path("2F650631682090A674BBB3CDBD3A080381C2E37B4B58DB40878FE5AD94635D4E/accounts/", include("accounts.urls")),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    url('^((?!media).)*$', TemplateView.as_view(template_name='index.html')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)