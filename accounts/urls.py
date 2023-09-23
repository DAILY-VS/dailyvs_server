from django.urls import path, include ,re_path
from django.views.generic import TemplateView
from .views import *

app_name = "accounts"

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # path('allauth/', include('allauth.urls')),
    # path('kakao/login/', kakao_login, name='kakao_login'),
    # path('kakao/login/callback/', kakao_callback, name='kakao_callback'),
    # path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
]

urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]