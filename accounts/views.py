import os
from django.shortcuts import render, redirect
import requests
from json import JSONDecodeError
from rest_framework import status
from .models import User
from config import local_settings
from rest_framework.response import Response
from rest_framework.decorators import api_view


from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from vote.models import Poll, UserVote

# 카카오 로그인 요청 (이건 나중에 프론트에서 할 예정)
def kakao_login(request):
    # 1. 인가 코드 받기 요청
    KAKAO_CALLBACK_URI = local_settings.BASE_URL + 'accounts/kakao/login/callback/'
    client_id = local_settings.SOCIAL_AUTH_KAKAO_CLIENT_ID
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email")
@api_view(['GET'])
def kakao_callback(request):
    BASE_URL = local_settings.BASE_URL
    KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/login/callback/'
    client_id = local_settings.SOCIAL_AUTH_KAKAO_CLIENT_ID
    # 4. 인가 코드 받기. (반드시 프론트에서 쿼리스트링으로 받아야 한다는데..?https://velog.io/@mechauk418/DRF-%EC%B9%B4%EC%B9%B4%EC%98%A4-%EC%86%8C%EC%85%9C-%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EA%B5%AC%ED%98%84%ED%95%98%EA%B8%B0-JWT-%EC%BF%A0%ED%82%A4-%EC%84%A4%EC%A0%95-%EB%B0%8F-%EC%A3%BC%EC%9D%98%EC%82%AC%ED%95%AD-CORS%EA%B4%80%EB%A0%A8)
    code = request.GET.get("code")

    # 5. 인가 코드로 access token 요청 (jwt 아님)
    token_request = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    token_response_json = token_request.json()
    # 에러 발생 시 중단
    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_response_json.get("access_token")

    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None) # 이메일!

    # 이메일 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능하다고 함...
    if email is None:
        return Response({'message': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 이메일 받아옴 -> 추가 정보 입력창 -> 받아서 기존 유저 로그인 방식대로 로그인?(비밀번호 없음)
    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # 이미 카카오로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return Response({'message': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        print("user exists")
        context = {
            'access': accept_json.pop('access'),
            'refresh': accept_json.pop('refresh'),
            'nickname': email.split('@')[0],
        }
        return Response(context)

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return Response({'message': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        print("user does not exist")
        context = {
            'access': accept_json.pop('access'),
            'refresh': accept_json.pop('refresh'),
            'nickname': email.split('@')[0],
        }
        return Response(context)


    
class KakaoLogin(SocialLoginView):
    print("hellloo")
    BASE_URL = local_settings.BASE_URL
    KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/login/callback/'
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI

from django.http import HttpResponseRedirect, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.views import ConfirmEmailView
from allauth.account import app_settings as allauth_settings

class MyConfirmEmailView(ConfirmEmailView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            if allauth_settings.CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except:
            self.object = None
            return redirect("http://localhost:3000/email-error/")

        return redirect("http://localhost:3000/login/")

    def post(self, request, *args, **kwargs):
        try:
            self.object = confirmation = self.get_object()
            confirmation.confirm(self.request)
            return redirect("http://localhost:3000/login/")
        except:
            # print("잘못된 key이거나 이미 인증된 메일, 기타등등")
            return redirect("http://localhost:3000/email-error/")

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

from dj_rest_auth.views import PasswordResetConfirmView
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

@api_view(['GET'])
def MyPageInfo(request):
    user = request.user
    voted_polls = []
    v_app = voted_polls.append
    print(user.voted_polls)
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

from allauth.account.models import EmailAddress
from django.test.client import Client
from django.urls import reverse
import time
def create_test_user(request):
    c = Client()
    for i in range(10):
        resp = c.post(
            reverse("rest_register"),
            {
                "email": f"test{i}@example.com",
                "password1": "qkrtlsqls12**",
                "password2": "qkrtlsqls12**",
                "nickname": "asdf",
                "gender": "M",
                "mbti": "ISTP",
                "age": "10"
            },
            follow=True,
        )
        new_user = EmailAddress.objects.get(email=f"test{i}@example.com")
        new_user.verified = True
        new_user.save()
        time.sleep(0.2)
    return redirect('/')

def delete_test_user(request):
    for i in range(10):
        user = User.objects.filter(email=f"test{i}@example.com")
        user.delete()
        time.sleep(0.2)
    return redirect('/')