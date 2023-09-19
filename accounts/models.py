from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, gender, mbti, password=None):
        if not email:
            raise ValueError('이메일 필수')
        
        email = self.normalize_email(email) # 소문자로 바꿈 + ?
        user = self.model(email=email, nickname=nickname, gender=gender, mbti=mbti)

        user.set_password(password)
        user.save()

        return user
        
    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email,
            nickname="",
            gender="",
            mbti="",
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
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
    
    email = models.EmailField(max_length=255, unique=True)
    nickname = models.CharField(max_length=10)
    gender = models.CharField(verbose_name="성별", max_length=1, choices=GENDERS)
    mbti=models.CharField(verbose_name='MBTI', max_length=4, choices=MBTI_set)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    voted_polls = models.ManyToManyField('vote.Poll', blank=True) #투표한 주제 리스트 
    custom_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'gender', 'mbti']

    def __str__(self):
        return self.email