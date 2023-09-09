from django.db import models
from django.contrib.auth.models import AbstractUser

# 유저 DB
class User(AbstractUser):  
    GENDERS = (
        ("M", "남성(Man)"),
        ("W", "여성(Woman)"),
    )
    gender = models.CharField(verbose_name="성별", max_length=1, choices=GENDERS)
    nickname = models.CharField(max_length=10)
    email = models.CharField(max_length=30)
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
    mbti=models.CharField(verbose_name='MBTI', max_length=4, choices=MBTI_set)
    nickname = models.CharField(verbose_name='닉네임',max_length=10)
    voted_polls = models.ManyToManyField('vote.Poll', blank=True) #투표한 주제 리스트 
    custom_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
