from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

import os
from io import BytesIO
from PIL import Image
from django.core.files import File

# Image compression method
def compress_image(image, size=(1000, 1000)):
    temp_image = Image.open(image).convert('RGB')
    temp_image.thumbnail(size)
    temp_image_io = BytesIO()
    temp_image.save(temp_image_io, 'jpeg', quality=50)
    new_image = File(temp_image_io, name=image.name)
    return new_image
# size=(1000, 1000)
# -> 원본 비율을 유지하면서 가로 세로 중 큰 값을 1000px 로 리사이즈

class Poll(models.Model):
    title = models.TextField()
    content = models.TextField()
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    poll_like = models.ManyToManyField(
        'accounts.User',
        related_name='poll_like',
        blank=True
    )
    views_count = models.PositiveIntegerField(default=0, null=True)  # 조회수
    thumbnail = models.ImageField(upload_to="thumbnails/%Y/%m/%d")
    comments_count = models.PositiveIntegerField(default=0, null=True, blank=True)  # 댓글 수
    created_at = models.DateTimeField(default=timezone.now)
    category = models.ManyToManyField('Category')
    choices = models.ManyToManyField('Choice')
    total_count = models.IntegerField(default = 0, null= True) #투표 수
    report_count = models.IntegerField(default = 0)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        new_thumbnail = compress_image(self.thumbnail)
        self.thumbnail = new_thumbnail
        super().save(*args, **kwargs)

# 투표 선택지
class Choice(models.Model):
    choice_text = models.CharField(max_length=255)
    choice_number = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

# 투표 정보 저장
class UserVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    gender = models.CharField(verbose_name="성별", max_length=1, null= True)
    mbti=models.CharField(verbose_name='MBTI', max_length=4, null= True)
    age = models.CharField(verbose_name='나이', max_length=4, null= True)

    def __str__(self):
        return self.poll.title

# 투표 별 카테고리
class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

# 투표 결과 저장
class Poll_Result(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE)
    total_count = models.IntegerField(default=0)
    choice_count = models.IntegerField(default=0)
    choice1 = models.BinaryField(editable=True, default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    choice2 = models.BinaryField(editable=True, default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    choice3 = models.BinaryField(editable=True, default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    choice4 = models.BinaryField(editable=True, default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    choice5 = models.BinaryField(editable=True, default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

# 댓글
class Comment(models.Model):
    user_info = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey('Choice', on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    parent_comment = models.ForeignKey('self', related_name='reply', on_delete=models.CASCADE, null=True, blank=True)  # 대댓글
    likes_count = models.PositiveIntegerField(default=0, null=True, blank=True)  # 좋아요 수
    report_count = models.IntegerField(default=0)
    comment_like = models.ManyToManyField(
        'accounts.User',
        related_name='comment_like',
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

class Today_Poll(models.Model):
    choice1 = models.ImageField(upload_to="choice1/%Y/%m/%d")
    choice2 = models.ImageField(upload_to="choice2/%Y/%m/%d")
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

class Poll_Report(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    content = models.CharField(max_length=100, null=True)

class Comment_Report(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    content = models.CharField(max_length=100, null=True)