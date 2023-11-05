from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls), 
    path("api/", include("vote.urls")), #vote app
    path("api/accounts/", include("accounts.urls")),
    re_path(r'^static/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_ROOT }),
    re_path('^((?!media).)*$', TemplateView.as_view(template_name='index.html')),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)