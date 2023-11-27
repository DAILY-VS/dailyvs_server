from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer


class CustomRegisterSerializer(RegisterSerializer):
    GENDERS = (
        ("M", "남성(Man)"),
        ("W", "여성(Woman)"),
    )
    MBTI_set = (
        ("INFP", "INFP"),
        ("ENFP", "ENFP"),
        ("INFJ", "INFJ"),
        ("ENFJ", "ENFJ"),
        ("INTJ", "INTJ"),
        ("ENTJ", "ENTJ"),
        ("INTP", "INTP"),
        ("ENTP", "ENTP"),
        ("ISFP", "ISFP"),
        ("ESFP", "ESFP"),
        ("ISFJ", "ISFJ"),
        ("ESFJ", "ESFJ"),
        ("ISTP", "ISTP"),
        ("ESTP", "ESTP"),
        ("ISTJ", "ISTJ"),
        ("ESTJ", "ESTJ"),
    )
    AGE_CHOICES = (
		("10", "10대"),
		("20_1", "20대 초반"),
		("20_2", "20대 후반"),
		("30_1", "30대 초반"),
		("30_2", "30대 후반"),
		("40", "40대 이상"),
	)
    nickname = serializers.CharField(max_length=10)
    gender = serializers.ChoiceField(GENDERS)
    mbti = serializers.ChoiceField(MBTI_set)
    age = serializers.ChoiceField(AGE_CHOICES)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')
        data['gender'] = self.validated_data.get('gender', '')
        data['mbti'] = self.validated_data.get('mbti', '')
        data['age'] = self.validated_data.get('age', '')

        return data



class CustomLoginSerializer(LoginSerializer):
    email = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})

from dj_rest_auth.forms import AllAuthPasswordResetForm
from django.conf import settings

class CustomPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    reset_form = None

    @property
    def password_reset_form_class(self):
        return AllAuthPasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)      
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        from allauth.account.forms import default_token_generator

        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'token_generator': default_token_generator,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)