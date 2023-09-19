from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from accounts.models import User

#투표 게시글 DB
class Poll(models.Model): 
    owner = models.ForeignKey(User, on_delete=models.CASCADE,)
    title = models.TextField()
    content = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    poll_like = models.ManyToManyField('accounts.User', blank=True, related_name='likes')
    views_count = models.PositiveIntegerField(default=0)  # 조회 수
    thumbnail = models.ImageField()
    comments = models.PositiveIntegerField(verbose_name='댓글수', default=0)  # 댓글 수    

    def increase_views(self): # 조회수
        self.views_count=self.views_count+1
        self.save()

    # def update_comments_count(self): # 댓글수
    #     self.comments = Comment.objects.filter(poll=self).count()
    #     self.save()
        
    def __str__(self):
        return self.title
    
#투표 선택지 DB
class Choice(models.Model) :
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    image = models.ImageField() 

#회원투표 DB
class UserVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_votes')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

#비회원투표
class NonUserVote(models.Model):
    MBTI = models.TextField(null= True)
    GENDERS = (
        ('M', '남성'),
        ('W', '여성'),
    )
    gender = models.CharField(verbose_name='성별', max_length=1, choices=GENDERS, null= True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

#댓글 DB
class Comment(models.Model): 
    user_info = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    comment_like = models.ManyToManyField('accounts.User', blank=True, related_name='comment_like')
   
    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None  # 새로운 댓글인지 확인
    #     super().save(*args, **kwargs)
        
    #     if is_new:  # 새로운 댓글인 경우 댓글 수 업데이트
    #         self.poll.update_comments_count()

    # def delete(self, *args, **kwargs):
    #     super().delete(*args, **kwargs)
    #     self.poll.update_comments_count()
   
    def __str__(self):
        return self.content
    
class Poll_Result(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    total= models.PositiveIntegerField(default=0)
    choice1_man=models.PositiveIntegerField(default=0)
    choice2_man=models.PositiveIntegerField(default=0)
    choice1_woman=models.PositiveIntegerField(default=0)
    choice2_woman=models.PositiveIntegerField(default=0)
    choice1_E=models.PositiveIntegerField(default=0)
    choice2_E=models.PositiveIntegerField(default=0)
    choice1_I=models.PositiveIntegerField(default=0)
    choice2_I=models.PositiveIntegerField(default=0)
    choice1_N=models.PositiveIntegerField(default=0)
    choice2_N=models.PositiveIntegerField(default=0)
    choice1_S=models.PositiveIntegerField(default=0)
    choice2_S=models.PositiveIntegerField(default=0)
    choice1_T=models.PositiveIntegerField(default=0)
    choice2_T=models.PositiveIntegerField(default=0)
    choice1_F=models.PositiveIntegerField(default=0)
    choice2_F=models.PositiveIntegerField(default=0)
    choice1_J=models.PositiveIntegerField(default=0)
    choice2_J=models.PositiveIntegerField(default=0)
    choice1_P=models.PositiveIntegerField(default=0)
    choice2_P=models.PositiveIntegerField(default=0)