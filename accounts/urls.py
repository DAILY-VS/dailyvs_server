from django.urls import path, include ,re_path
from django.views.generic import TemplateView
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView, PasswordChangeView
from .views import *

urlpatterns = [
    # path('', measure_time),

    path('', include('dj_rest_auth.urls')),
    path('', include('dj_rest_auth.registration.urls')),

    # 유효한 이메일이 유저에게 전달
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('user_info/', UserInfo),
    path('mypage_info/', MyPageInfo),

    path('allauth/', include('allauth.urls')),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/callback/', kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
]