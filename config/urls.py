from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from accounts.views import MyConfirmEmailView

urlpatterns = [
    path("admin/", admin.site.urls), 
    path("", include("vote.urls")), #vote app
    path("accounts/", include("accounts.urls")),
    re_path(r'^register/(?P<key>[-:\w]+)/$', MyConfirmEmailView.as_view(), name='account_confirm_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)