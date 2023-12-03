import os
from django.shortcuts import redirect
import requests
from rest_framework import status
from .models import User
from config.settings.base import local_settings
from config.settings import base
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status


from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from vote.models import Poll, UserVote
from dj_rest_auth.models import get_token_model
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.serializers import JWTSerializer

class KakaoLoginView(APIView):
    serializer_class = SocialLoginSerializer
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request):
        code = request.data.get('code')
        access_token = request.data.get("access")

        BASE_URL = local_settings.BASE_URL
        # access token으로 카카오톡 프로필 요청
        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)
        if email is None:
            return Response({'message': 'fail'}, status=status.HTTP_400_BAD_REQUEST)
        # 이메일 받아옴 -> 추가 정보 입력창 -> 받아서 기존 유저 로그인 방식대로 로그인?(비밀번호 없음)
        # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
        user = User.objects.filter(email=email)
        if user:
            # 전달받은 이메일로 등록된 유저가 있는지 탐색
            user = user[0]
            # 기존 로그인 회원인 경우
            if user.is_kakao == False:
                raise
                return Response({"message": "existing user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # 이미 카카오로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
            data = {'access_token': access_token, 'code': code}
            # accept = requests.post(f"{BASE_URL}/accounts/kakao/login/finish/", data=data)
            accept = self.custom_login(data=data)
            accept_status = accept.status_code
            # 뭔가 중간에 문제가 생기면 에러
            if accept_status != 200:
                return Response({'message': 'fail'}, status=accept_status)
            context = {
                'access': accept.data['access'],
                'refresh': accept.data['refresh'],
            }
            return Response(context)
        else:
            # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
            data = {'access_token': access_token, 'code': code}
            # accept = requests.post(f"{BASE_URL}/accounts/kakao/login/finish/", data=data)
            accept = self.custom_login(data=data)
            accept_status = accept.status_code
            # 뭔가 중간에 문제가 생기면 에러
            if accept_status != 200:
                return Response({'message': 'fail'}, status=accept_status)
            user = User.objects.get(email=email)
            user.nickname = "user" + str(user.id)
            user.is_kakao = True
            user.save()
            context = {
                'access': accept.data['access'],
                'refresh': accept.data['refresh'],
            }
            return Response(context)
    def login(self):
        self.user = self.serializer.validated_data['user']
        token_model = get_token_model()
        self.access_token, self.refresh_token = jwt_encode(self.user)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = SocialLoginSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def get_response(self):
        serializer_class = JWTSerializer

        data = {
            'user': self.user,
            'access': self.access_token,
        }

        data['refresh'] = self.refresh_token

        serializer = serializer_class(
            instance=data,
            context=self.get_serializer_context(),
        )

        response = Response(serializer.data, status=status.HTTP_200_OK)

        from dj_rest_auth.jwt_auth import set_jwt_cookies
        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response
    
    def custom_login(self, data):
        self.serializer = self.get_serializer(data=data)
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()

@api_view(['POST'])
def logout_with_kakao(request):
    try:

        REST_API_KEY = local_settings.SOCIAL_AUTH_KAKAO_CLIENT_ID
        access_kakao = request.data.get('access_kakao')
        headers = {"Authorization": f'Bearer {access_kakao}'}
        logout_response = requests.post('https://kapi.kakao.com/v1/user/logout', headers=headers)

        refresh = request.data.get('refresh')
        body = {"refresh": f'{refresh}'}
        daily_logout_response = requests.post(f'{local_settings.BASE_URL}/accounts/logout/', data=body)
    except:
        return Response({'message':'fail'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message':'success'}, status=status.HTTP_200_OK)

from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.views   import ConfirmEmailView
from allauth.account import app_settings as allauth_settings

class MyConfirmEmailView(ConfirmEmailView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        FRONT_BASE_URL = local_settings.FRONT_BASE_URL
        try:
            self.object = self.get_object()
            if allauth_settings.CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except:
            self.object = None
            return redirect(f"{FRONT_BASE_URL}/email-error/")

        return redirect(f"{FRONT_BASE_URL}/login/")

    def post(self, request, *args, **kwargs):
        FRONT_BASE_URL = local_settings.FRONT_BASE_URL
        try:
            self.object = confirmation = self.get_object()
            confirmation.confirm(self.request)
            return redirect(f"{FRONT_BASE_URL}/login/")
        except:
            # print("잘못된 key이거나 이미 인증된 메일, 기타등등")
            return redirect(f"{FRONT_BASE_URL}/email-error/")

        return self.respond(True)

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                return HttpResponseRedirect('/') # 인증실패
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
class MyPasswordResetConfirmView(PasswordResetConfirmView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'message': 'success'},
            )
        except:
            return Response({'message':'fail'})

from .serializers import CustomPasswordResetSerializer
class MyPasswordResetView(PasswordResetView):
    serializer_class = CustomPasswordResetSerializer
    permission_classes = (AllowAny,)
    throttle_scope = 'dj_rest_auth'

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        email = request.data.get('email')

        # 비밀번호 변경의 경우
        if request.user.is_authenticated:
            user = request.user
            if user.email != email:
                return Response({'message':'wrong'}, status=522)
            if user.is_kakao:
                return Response({'message':'kakao user'}, status=521)
        
        # 비밀번호 재설정의 경우
        else:
            user = User.objects.filter(email=email)
            # 회원가입한 이메일이 아닌 경우
            if not user:
                return Response({'message':'invalid'}, status=520)
            # 카카오 유저인 경우
            user = user[0]
            if user.is_kakao:
                return Response({'message':'kakao user'}, status=521)
            
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid()
        except:
            return Response({'message':'fail'}, status=523)
        serializer.save()
        # Return the success message with OK HTTP status
        return Response({'message': 'success'}, status=200)

@api_view(['GET'])
def MyPageInfo(request):
    user = request.user
    voted_polls = []
    v_app = voted_polls.append
    for poll_n in user.voted_polls.all():
        poll = Poll.objects.get(id=poll_n.id)
        v_app({
            "id": poll.id,
            "title": poll.title,
            "owner_id": poll.owner.id,
            "owner": poll.owner.nickname,
            "thumbnail": poll.thumbnail.url,
            "choice": UserVote.objects.get(user=user, poll=poll.id).choice.choice_text,
        })

    context = {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "gender": user.gender,
        "mbti": user.mbti,
        "age": user.age,
        "voted_polls": voted_polls
    }
    return Response(context)

@api_view(['GET'])
def UserInfo(request):
    user = request.user
    context = {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "gender": user.gender,
        "mbti": user.mbti,
        "age": user.age,
    }
    return Response(context)

class DeleteAccount(APIView):
    def delete(self, request):
        user=request.user
        if user.is_authenticated:
            try:
                # 카카오 유저인 경우 카카오와 연결 끊기 먼저 진행.
                if user.is_kakao:
                    access_kakao = request.data.get('access_kakao')
                    headers = {"Authorization": f'Bearer {access_kakao}'}
                    unlink_response = requests.post('https://kapi.kakao.com/v1/user/unlink', headers=headers)
                
                self.logout(request)
                user.delete()

                response = Response(
                    {"message": "success"},
                    status=status.HTTP_200_OK,
                )

                cookie_name1 = base.REST_AUTH['JWT_AUTH_COOKIE']
                cookie_name2 = base.REST_AUTH['JWT_AUTH_REFRESH_COOKIE']
                response.delete_cookie(cookie_name1)
                response.delete_cookie(cookie_name2)

                return response
            except:
                return Response({'message':'fail'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": "fail"}, status=status.HTTP_401_UNAUTHORIZED)

    def logout(self, request):
        from rest_framework_simplejwt.exceptions import TokenError
        from rest_framework_simplejwt.tokens import RefreshToken
        from dj_rest_auth.jwt_auth import unset_jwt_cookies
        from django.utils.translation import gettext_lazy as _

        response = Response(
            {'detail': _('Successfully logged out.')},
            status=status.HTTP_200_OK,
        )
        
        cookie_name = base.REST_AUTH['JWT_AUTH_COOKIE']
        unset_jwt_cookies(response)
        if 'rest_framework_simplejwt.token_blacklist' in base.INSTALLED_APPS:
            # add refresh token to blacklist
            try:
                token = RefreshToken(request.data['refresh'])
                token.blacklist()
            except KeyError:
                response.data = {'detail': _('Refresh token was not included in request data.')}
                response.status_code =status.HTTP_401_UNAUTHORIZED
            except (TokenError, AttributeError, TypeError) as error:
                if hasattr(error, 'args'):
                    if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                        response.data = {'detail': _(error.args[0])}
                        response.status_code = status.HTTP_401_UNAUTHORIZED
                    else:
                        response.data = {'detail': _('An error has occurred.')}
                        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                else:
                    response.data = {'detail': _('An error has occurred.')}
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        elif not cookie_name:
            message = _(
                'Neither cookies or blacklist are enabled, so the token '
                'has not been deleted server side. Please make sure the token is deleted client side.',
            )
            response.data = {'detail': message}
            response.status_code = status.HTTP_200_OK
        return response