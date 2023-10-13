from rest_framework import serializers #추가
from .models import *

#Serializer : DRF가 제공하는 클래스, DB 인스턴스를 JSON 데이터로 생성한다.

class PollSerializer(serializers.ModelSerializer):
    
    thumbnail= serializers.ImageField(use_url=True)
    class Meta:
        model = Poll
        fields = '__all__'

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class UserVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVote
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
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
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender', 'mbti']

class CommentLikeSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField()
    user_id = serializers.IntegerField()