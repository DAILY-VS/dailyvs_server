from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        # 기본 저장 필드: first_name, last_name, username, email
        user = super().save_user(request, user, form, False)
        # 추가 저장 필드: profile_image
        nickname = data.get("nickname")
        if nickname:
            user.nickname = nickname

        gender = data.get("gender")
        if gender:
            user.gender = gender

        mbti = data.get("mbti")
        if mbti:
            user.mbti = mbti

        age = data.get("age")
        if age:
            user.age = age

        user.save()
        return user
    
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = settings.CUSTOM_ACCOUNT_CONFIRM_EMAIL_URL.format(emailconfirmation.key)
        ret = build_absolute_uri(
            request,
            url)
        return ret