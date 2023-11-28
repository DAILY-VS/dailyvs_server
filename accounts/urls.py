from django.urls import path, include ,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetView, PasswordChangeView
from .views import *

urlpatterns = [
    # path('', measure_time),
    path('', include('dj_rest_auth.urls')),
    path('', include('dj_rest_auth.registration.urls')),

    # 유효한 이메일이 유저에게 전달
    re_path(r'^allauth/confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^allauth/confirm-email/(?P<key>[-:\w]+)/$', MyConfirmEmailView.as_view(), name='account_confirm_email'),
    path('password/reset/confirm/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('delete/', DeleteAccount.as_view()),

    path('user_info/', UserInfo),
    path('mypage_info/', MyPageInfo),

    path('allauth/', include('allauth.urls')),
    path('kakao/login/callback/', KakaoLoginView.as_view(), name='kakao_callback'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),

    path('test/user/create/', create_test_user),
    path('test/user/delete/', delete_test_user),
]+ static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)