from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import RegexValidator

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        label="이메일",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "이메일 주소"}),
    )
    username = forms.CharField(
        label="아이디",
        max_length=10,
        min_length=5,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]*$',
                message='영어와 숫자만 사용할 수 있습니다.',
            )
        ],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "아이디 (5자 이상 10자 이하)"}
        ),
    )
    password1 = forms.CharField(
        label="비밀번호",
        max_length=15,
        min_length=5,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "비밀번호 (8자 이상 15자 이하)"}
        ),
    )
    password2 = forms.CharField(
        label="확인 비밀번호",
        max_length=15,
        min_length=5,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "비밀번호 확인"}
        ),
    )

    gender_choices = [
        ("M", "남성(Man)"),
        ("W", "여성(Woman)"),
    ]

    gender = forms.ChoiceField(
        label="성별",
        choices=gender_choices,
        widget=forms.RadioSelect(attrs={"class": "radio-list"}),
    )

    MBTI_CHOICES = [
        ('INFP', 'INFP'), ('ENFP', 'ENFP'), ('INFJ', 'INFJ'), ('ENFJ', 'ENFJ'),
        ('INTJ', 'INTJ'), ('ENTJ', 'ENTJ'), ('INTP', 'INTP'), ('ENTP', 'ENTP'),
        ('ISFP', 'ISFP'), ('ESFP', 'ESFP'), ('ISFJ', 'ISFJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ESTP', 'ESTP'), ('ISTJ', 'ISTJ'), ('ESTJ', 'ESTJ'),
    ]

    mbti = forms.ChoiceField(
        label="MBTI",
        choices=MBTI_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다.")
        return nickname
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email
    
    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2", "mbti", "nickname", "gender"]
        widgets = {
            "mbti": forms.Select(
                attrs={"class": "form-control", "placeholder": "MBTI (대문자로 ex.INFP)"}
            ),
            "nickname": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "닉네임 (2자 이상 10자 이하)"}
            ),
        }

class UserChangeForm(UserChangeForm):
    password = None
    gender_choices = [
        ("M", "남성(Man)"),
        ("W", "여성(Woman)"),
    ]

    gender = forms.ChoiceField(
        label="성별",
        choices=gender_choices,
        widget=forms.RadioSelect(attrs={"class": "radio-list"}),
    )

    MBTI_CHOICES = [
        ('INFP', 'INFP'), ('ENFP', 'ENFP'), ('INFJ', 'INFJ'), ('ENFJ', 'ENFJ'),
        ('INTJ', 'INTJ'), ('ENTJ', 'ENTJ'), ('INTP', 'INTP'), ('ENTP', 'ENTP'),
        ('ISFP', 'ISFP'), ('ESFP', 'ESFP'), ('ISFJ', 'ISFJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ESTP', 'ESTP'), ('ISTJ', 'ISTJ'), ('ESTJ', 'ESTJ'),
    ]

    mbti = forms.ChoiceField(
        label="MBTI",
        choices=MBTI_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        user_model = get_user_model()
        # 현재 이름과 같다면 상관없이 PASS
        user_instance = self.instance
        # 다른 유저랑 이름이 같다면 제한
        other_users_with_same_nickname = user_model.objects.exclude(id=user_instance.id).filter(nickname=nickname)
        if other_users_with_same_nickname.exists():
            raise forms.ValidationError("이미 사용 중인 닉네임입니다.")
        return nickname
    
    class Meta:
        model = User
        fields = ["mbti", "nickname", "gender"]
        widgets = {
            "mbti": forms.Select(
                attrs={"class": "form-control", "placeholder": "MBTI (대문자로 ex.INFP)"}
            ),
            "nickname": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "별명을 입력하세요"}
            ),
        }


class UserDeleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []


class EmailForm(forms.Form):
    email = forms.EmailField(label="이메일", max_length=30, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "이메일 주소"}))



class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label='비밀번호',
        max_length=15,
        min_length=5,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "비밀번호 (5자 이상 15자 이하)"}
        ),       
        )
    confirm_new_password = forms.CharField(
        label='새 비밀번호',
        max_length=15,
        min_length=5,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "비밀번호 확인"}
        ),       
        )
 