import os
from django.shortcuts import render, redirect
import requests
from json import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status
from .models import User, Test
from config import local_settings

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

# 카카오 로그인 요청 (이건 나중에 프론트에서 할 예정)
def kakao_login(request):
    # 1. 인가 코드 받기 요청
    KAKAO_CALLBACK_URI = local_settings.BASE_URL + 'accounts/kakao/login/callback/'
    client_id = local_settings.SOCIAL_AUTH_KAKAO_CLIENT_ID
    print(client_id)
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email")

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
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    print(email)
    
    # 이메일 받아옴 -> 추가 정보 입력창 -> 받아서 기존 유저 로그인 방식대로 로그인?(비밀번호 없음)
    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 우저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


    
class KakaoLogin(SocialLoginView):
    BASE_URL = local_settings.BASE_URL
    KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/login/callback/'
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI

from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC

class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # A React Router Route will handle the failure scenario
        return HttpResponseRedirect('/') # 인증성공

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                # A React Router Route will handle the failure scenario
                return HttpResponseRedirect('/') # 인증실패
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs


# import math
# import time
# def measure_time(request):
#     start = time.time()
#     # 80번 get
#     for i in range(16*500):
#         user = Test.objects.get(id=2)
#     end = time.time()
#     print(f"{end - start:.5f} sec")

#     # 1번 get, 1번 파싱
#     res = []
#     start = time.time()
#     # test_byte = b'\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10'
#     # print(test_byte)
#     # testobject = Test.objects.create(a=test_byte)
#     # testobject.save()
#     for j in range(500):
#         data = Test.objects.get(id=6)
#         binary = bytes(data.a)
#         # print(int.from_bytes(binary[0:4], byteorder='big', signed=False))
#         # print(binary[0:4])
#         for i in range(16):
#             tmp = int.from_bytes(binary[0 + 4 * i : 4 + 4 * i], byteorder='big', signed=False)
#             # print(tmp)
#             res.append(tmp)
#     end = time.time()
#     # print(res)
#     print(f"{end - start:.5f} sec")
