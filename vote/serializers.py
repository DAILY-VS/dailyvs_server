from rest_framework import serializers #추가
from .models import *
from accounts.models import User
from datetime import datetime
import math

#Serializer : DRF가 제공하는 클래스, DB 인스턴스를 JSON 데이터로 생성한다.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'age', 'gender', 'mbti']
        
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
class PollSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    choices = ChoiceSerializer(many=True)
    category = CategorySerializer(many=True)

    class Meta:
        model = Poll
        fields = '__all__'

class PollCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    class Meta:
        model = Poll
        fields = '__all__'
    def create(self, validated_data): #choice 중첩 문제로 오버라이딩
        choices_data = validated_data.pop('choices')
        poll = Poll.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(poll=poll, **choice_data)
        return poll

class TodayPollSerializer(serializers.ModelSerializer):
    poll = PollSerializer(many=False)
    class Meta:
        model = Today_Poll
        fields = '__all__'

class UserVoteSerializer(serializers.ModelSerializer):
    choice = ChoiceSerializer(many=False)
    poll = PollSerializer(many=False)
    class Meta:
        model = UserVote
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user_info = UserSerializer()
    time_difference = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    choice_text = serializers.CharField(source='choice.choice_text', read_only=True)
    
    def get_reply(self, obj):  # 대댓글
        replies = Comment.objects.filter(parent_comment=obj)
        for comment in replies:
            choice_id = comment.choice_id
            if choice_id:
                choice = Choice.objects.get(pk=choice_id)
                comment.choice_text = choice.choice_text
        return CommentSerializer(replies, many=True).data
    
    def get_time_difference(self, obj): #클라이언트에게 넘겨줄 시간차이(-전)
        now = datetime.now()
        time_difference = now - obj.created_at
        seconds = time_difference.total_seconds() #초로변환
        
        if seconds < 60: #몇초 전
            return f"{math.trunc(seconds)}초 전"
        elif seconds < 3600: #몇분 전
            return f"{math.trunc(seconds / 60)}분 전"
        elif seconds < 86400: #몇시간 전 (60*60*24)
            return f"{math.trunc(seconds / 3600)}시간 전"
        elif seconds < 604800: #몇일 전 (60*60*24*7)
            return f"{math.trunc(seconds / 86400)}일 전"
        elif seconds < 2419200: #몇달 전 (60*60*24*7*30)
            return f"{math.trunc(seconds / 604800)}주 전"
        elif seconds < 29030400:  #몇달 전 (60*60*24*7*30)
            return f"{math.trunc(seconds / 2419200)}달 전"
        else: #몇년 전
            return f"{math.trunc(seconds / 29030400)}년 전"
        
    class Meta:
        model = Comment
        fields = '__all__'

class PollResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll_Result
        fields = '__all__'
        
class PollLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
