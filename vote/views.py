import json, random
from .models import *
from .fortunes import fortunes
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework.decorators import api_view, parser_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import *
from itertools import chain


# 메인페이지
class MainViewSet(ModelViewSet):
    serializer_class = PollSerializer
    def list(self, request, *args, **kwargs):
        polls = Poll.objects.all().order_by('-id')
        today_poll = Today_Poll.objects.first()
        if today_poll:
            serialized_today_poll = TodayPollSerializer(today_poll, context={'request': request}).data
        else:
            serialized_today_poll = None

        hot_polls = Poll.objects.filter(total_count__gte=10).order_by('-id')
        mbti_polls = Poll.objects.filter(category__name='mbti').order_by('-id')
        gender_polls = Poll.objects.filter(category__name='gender').order_by('-id')
        age_polls = Poll.objects.filter(category__name='age').order_by('-id')

        serialized_polls = self.get_serializer(polls, many=True).data
        serialized_hot_polls = self.get_serializer(hot_polls, many=True).data
        serialized_mbti_polls = self.get_serializer(mbti_polls, many=True).data
        serialized_gender_polls = self.get_serializer(gender_polls, many=True).data
        serialized_age_polls = self.get_serializer(age_polls, many=True).data

        context = {
            "polls": serialized_polls,
            "hot_polls": serialized_hot_polls,
            "today_poll": serialized_today_poll,
            "mbti_polls" : serialized_mbti_polls,
            "gender_polls" : serialized_gender_polls,
            "age_polls" : serialized_age_polls,
        }
        return Response(context)

@api_view(['GET'])
def event(request):
    top_users = User.objects.order_by('-point')[:10]

    serialized_top_users = TopUserSerializer(top_users, many=True).data

    for user_data in serialized_top_users:
        user = User.objects.get(id=user_data['id'])
        
        most_recent_poll = Poll.objects.filter(owner=user).order_by('-created_at').first()

        if most_recent_poll:
            serialized_poll = PollSerializer(most_recent_poll).data
            user_data['most_recent_poll'] = serialized_poll
        else:
            user_data['most_recent_poll'] = None


    event_description = '''본인이 올린 투표 주제에 사람들이 투표할 때마다 VS POINT 획득! 
    서버 내 첫 100, 2000, 50000 포인트 달성 시 다음 과 같은 상금 지급!’
    1000 포인트 (5명)

    - 4500원 기프티콘

    2000 포인트 (3명)

    - 10000원 기프티콘

    20000 포인트 (1명)

    - 5만원 현금 지급
    ※비정상적인 방법 사용 적발 시 상품이 미지급 될 수 있습니다.
    '''

    context = {
        'event_description':event_description,
        'top_users': serialized_top_users,
    }
    return Response(context)

#검색 기능
class MainViewSearch(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset

@api_view(['GET'])
def comment_delete(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if request.user == comment.user_info:
        comment.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)
    else:
        return Response("fail", status=status.HTTP_403_FORBIDDEN)

#투표 만들기
@api_view(['POST'])
@parser_classes([MultiPartParser])
def poll_create(request):
    thumbnail = request.FILES.get('thumbnail')
    title = request.data.get('title')
    content = request.data.get('content')
    categories = request.data.getlist('category') 
    choices = request.data.getlist('choice')
    owner = request.user

    if not(thumbnail):
        return Response({"error": "이미지를 업로드해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    elif not (title):
        return Response({"error": "제목을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    elif not (content):
        return Response({"error": "내용을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    elif (len(choices) < 2):
        return Response({"error": "선택지를 2개 이상 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    elif not (categories):
        return Response({"error": "카테고리를 선택해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    # elif not (title and content and categories and choices and owner and thumbnail):
    #     return Response({"error": "필수 데이터가 제공되어 있지 않음"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 카테고리 데이터 파싱
    category_ids = []
    for category_str in categories:
        try:
            category_data = json.loads(category_str.replace("'", "\""))
            category_id = category_data.get('id')
            if category_id is not None:
                category_ids.append(category_id)
        except (json.JSONDecodeError, KeyError):
            return Response({"error": "카테고리 데이터 형식이 아님."}, status=status.HTTP_400_BAD_REQUEST)

    # 선택지 데이터 파싱
    choice_data = []
    for choice_str in choices:
        try:
            choice_dict = json.loads(choice_str.replace("'", "\""))
            choice_data.append(choice_dict['choice_text'])
        except (json.JSONDecodeError, KeyError):
            return Response({"error": "선택지 데이터 형식이 아님."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Poll 객체 생성
    poll_data = {
        "title": title,
        "content": content,
        "thumbnail": thumbnail,
        "owner": owner,
    }
    poll = Poll.objects.create(**poll_data)
    
    # 카테고리 할당
    poll.category.set(category_ids)
    # 선택지 할당
    for i, choice_text in enumerate(choice_data):
        choice = Choice.objects.create(poll=poll, choice_text=choice_text, choice_number= i + 1)
        poll.choices.add(choice)

    serialized_poll = PollCreateSerializer(poll)
    return Response(serialized_poll.data, status=status.HTTP_200_OK)

# 투표 디테일 페이지
class PollDetailView(APIView):
    def get(self, request, poll_id):
        user = request.user
        #이미 투표한 경우 
        previous_choice = False
        previous_choice_id = False
        if user.is_authenticated and user.voted_polls.filter(id=poll_id).exists():
            try : 
                uservote = UserVote.objects.get(poll_id=poll_id, user=user)
                previous_choice = int(uservote.choice.choice_number)
                previous_choice_id = int(uservote.choice.id)
            except :
                previous_choice = False
                previous_choice_id = False

        poll = get_object_or_404(Poll, id=poll_id)
        serialized_poll = PollSerializer(poll, context={'request': request}).data

        categorys = serialized_poll.get('category', [])
        category_list = [category.get('name') for category in categorys]
        category_remove_list = []

        if user.is_authenticated : 
            for category_name in category_list:
                user_category_value = getattr(user, category_name, "")
                if user_category_value is not None:
                    category_remove_list.append(category_name)
        category_list = [category for category in category_list if category not in category_remove_list]
        
        is_owner = False 
        if user == poll.owner : 
            is_owner = True
        context = {
            "is_owner" : is_owner,
            "previous_choice" : previous_choice,
            "previous_choice_id" : previous_choice_id,
            "poll": serialized_poll,
            "category_list" : category_list,
        }
        return Response(context)
    
    # 투표 delete
    def delete(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)
        if request.user == poll.owner:
            poll.delete()
            return Response("success", status=status.HTTP_204_NO_CONTENT)
        else: 
            return Response("fail", status=status.HTTP_403_FORBIDDEN)

# 댓글 read
class CommentView(APIView, PageNumberPagination):
    pagination_class=PageNumberPagination
    page_size=5
    def get(self, request, poll_id, sort):
        # 댓글
        user = request.user
        if sort == 'newest':
            comments = Comment.objects.filter(poll_id=poll_id, parent_comment=None).order_by('-id')
        elif sort == 'popular':
            comments = Comment.objects.filter(poll_id=poll_id, parent_comment=None).order_by('-likes_count', '-id')
        else:
            comments = Comment.objects.filter(poll_id=poll_id, parent_comment=None).order_by('-id')
        comments_count = comments.count()
        comment_page=self.paginate_queryset(comments, self.request)
        serialized_comments = CommentSerializer(comment_page, many=True).data if comment_page is not None else CommentSerializer(comments, many=True).data
        
        #댓글 작성자와 일치 여부
        if user.is_authenticated : 
            for idx, comment in enumerate(serialized_comments):
                if user.nickname == comment['user_info']['nickname'] :
                    serialized_comments[idx] = comment | {'is_owner' : True}
                choice_id = comment.get('choice')
                if choice_id:
                    choice = Choice.objects.get(pk=choice_id)
                    comment['choice_text'] = choice.choice_text
                if comment['reply'] :
                    for idx2, reply in enumerate(comment['reply']) : 
                        if user.nickname == reply['user_info']['nickname'] :
                            serialized_comments[idx]['reply'][idx2] = reply | {'is_owner' : True}
                            
        context = {
            "comments": serialized_comments,
            "comments_count": comments_count
        }
        return Response(context, status=status.HTTP_200_OK)

#댓글 쓰기
@api_view(['POST'])
def comment_create(request, poll_id):
    choice = UserVote.objects.get(user=request.user, poll=poll_id).choice
    poll = poll_id
    user=request.user
    data= {
        **request.data,
        'choice': choice.id,
        'poll': poll,
    }
    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user_info=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 댓글 delete
@api_view(['DELETE'])
def comment_delete(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if request.user == comment.user_info:
        comment.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)
    else:
        return Response("fail", status=status.HTTP_403_FORBIDDEN)

# 투표 좋아요
class PollLikeView(APIView):
    def get(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)
        user = request.user
        user_likes_poll = poll.poll_like.filter(id=user.id).exists()
        
        if user_likes_poll:
            message = "like" #좋아요가 있음
        else:
            message = "unlike" #좋아요가 없음
        like_count = poll.poll_like.count()
        context = {
            "message": message,
            "like_count": like_count,
            "user_likes_poll": user_likes_poll #user_likes_comment가 True일 때 좋아요를 누르고 있는 상태
        }
        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)
        user = request.user
        user_likes_poll = poll.poll_like.filter(id=user.id).exists()
        if user_likes_poll:
            poll.poll_like.remove(user)
            message = "unlike" #좋아요가 있으므로 좋아요 취소
        else:
            poll.poll_like.add(user)
            message = "like" #좋아요가 없으므로 좋아요
        like_count = poll.poll_like.count()
        
        context = {
            "message": message,
            "like_count": like_count,
            "user_likes_poll": not user_likes_poll #user_likes_comment가 True일 때 좋아요를 누르고 있는 상태
        }
        return Response(context, status=status.HTTP_200_OK)

# 투표 신고
@api_view(['POST'])
def poll_report(request, poll_id):
    user = request.user
    if user.is_authenticated:
        try:
            poll = Poll.objects.get(id=poll_id)
        except:
            return Response({"message": "no poll"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            report = Poll_Report.objects.get(user=user, poll=poll)
            return Response({"message": "reported"}, status=status.HTTP_200_OK)
        except: 
            # 기존에 신고를 한 번도 안 한 경우
            try:
                content = request.data.get('content')
                report = Poll_Report.objects.create(user=user, poll=poll, content=content)
                Poll.objects.filter(pk=poll_id).update(report_count = poll.report_count +1)


                subject = "[DailyVS] 투표글 신고 접수" # 메일 제목
                to = ["spark2357@naver.com"] # 문의 내용을 보낼 메일 주소, 리스트 형식
                message = f"Poll_id: {poll_id}\n신고내용: {content}\n누적 신고수: {poll.report_count}\n확인 부탁드립니다." # 메일 내용

                EmailMessage(subject=subject, body=message, to=to).send() # 메일 보내기
                return Response({"message":"success"}, status=status.HTTP_200_OK)
            except:
                return Response({"message":"fail"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"fail"}, status=status.HTTP_401_Unauthorized)

# 댓글 좋아요
class CommentLikeView(APIView):
    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user
        user_likes_comment = comment.comment_like.filter(id=user.id).exists()
        
        if user_likes_comment:
            message = "like"
        else:
            message = "unlike"

        like_count = comment.comment_like.count()
        context = {
            "like_count": like_count,
            "message": message,
            "user_likes_comment": user_likes_comment
        }
        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "해당 댓글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user
        user_likes_comment = comment.comment_like.filter(id=user.id).exists()
        
        if user_likes_comment: #user가 좋아요를 누른 상태 -> 좋아요 취소 누르기
            comment.comment_like.remove(user)
            message = "unlike"
        else: #user가 좋아요 누르지 않은 상태 -> 좋아요 누르기
            comment.comment_like.add(user)
            message = "like"
        comment.likes_count = comment.comment_like.count()
        comment.save()
        likes_count=comment.comment_like.count()
        context = {
            "likes_count": likes_count,
            "message": message,
            "user_likes_comment": not user_likes_comment 
        }
        return Response(context, status=status.HTTP_200_OK)

# 댓글 신고
@api_view(['POST'])
def comment_report(request, comment_id):
    user = request.user
    if user.is_authenticated:
        try:
            comment = Comment.objects.get(id=comment_id)
        except:
            return Response({"message": "no comment"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            report = Comment_Report.objects.get(user=user, comment=comment)
            return Response({"message": "reported"}, status=status.HTTP_200_OK)
        except: 
            # 기존에 신고를 한 번도 안 한 경우
            try:
                content = request.data.get('content')
                report = Comment_Report.objects.create(user=user, comment=comment, content=content)
                comment.report_count += 1
                comment.save()

                subject = "[DailyVS] 투표글 신고 접수" # 메일 제목
                to = ["spark2357@naver.com"] # 문의 내용을 보낼 메일 주소, 리스트 형식
                message = f"Comment_id: {comment_id}\n신고내용: {content}\n누적 신고수: {comment.report_count}\n확인 부탁드립니다." # 메일 내용

                EmailMessage(subject=subject, body=message, to=to).send() # 메일 보내기
                return Response({"message":"success"}, status=status.HTTP_200_OK)
            except:
                return Response({"message":"fail"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"fail"}, status=status.HTTP_401_Unauthorized)

#마이페이지_내가한투표
class MypageUserVoteView(APIView, PageNumberPagination):
    pagination_class = PageNumberPagination
    page_size = 5
    def get(self, request):
        user = request.user
        #사용자의 투표 목록 가져오기
        if not user.is_authenticated:
            return Response("error", status=status.HTTP_401_Unauthorized) #unauthorized
        uservote = UserVote.objects.filter(user=request.user)
        uservote_page=self.paginate_queryset(uservote, self.request)
        uservote_serializer = UserVoteSerializer(uservote_page, many=True, context={'request': request}).data if uservote_page is not None else UserVoteSerializer(uservote, many=True, context={'request': request}).data

        uservote_count = uservote.count()
        
        context={
            "uservote":uservote_serializer,
            "uservote_count":uservote_count,
        }
        return Response(context)
    
#마이페이지_내가만든투표
class MypageMyPollView(APIView, PageNumberPagination):
    pagination_class = PageNumberPagination
    page_size = 5
    def get(self, request):
        user = request.user
        #사용자의 투표 목록 가져오기
        if not user.is_authenticated:
            return Response("error", status=status.HTTP_401_Unauthorized) #unauthorized
        my_poll = Poll.objects.filter(owner=request.user)
        my_poll_page = self.paginate_queryset(my_poll, self.request)
        my_poll_serializer = PollSerializer(my_poll_page, many=True, context={'request': request}).data if my_poll_page is not None else PollSerializer(my_poll, many=True, context={'request': request}).data
        
        my_poll_count = my_poll.count()
        
        context={
            "my_poll":my_poll_serializer,
            "my_poll_count":my_poll_count,
        }
        return Response(context)

#마이페이지_내가좋아요한투표
class MypagePollLikeView(APIView, PageNumberPagination):
    pagination_class = PageNumberPagination
    page_size = 5
    def get(self, request):
        user = request.user
        #사용자의 투표 목록 가져오기
        if not user.is_authenticated:
            return Response("error", status=status.HTTP_401_Unauthorized) #unauthorized
        poll_like = Poll.objects.filter(poll_like=request.user)
        poll_like_page = self.paginate_queryset(poll_like, self.request)
        poll_like_serializer = PollSerializer(poll_like_page, many=True, context={'request': request}).data if poll_like_page is not None else PollSerializer(poll_like, many=True, context={'request': request}).data
        
        poll_like_count = poll_like.count()
        
        context={
            "poll_like_count": poll_like_count,
            "poll_like":poll_like_serializer,
        }
        return Response(context)

#마이페이지 개인정보
class MypageView(APIView, PageNumberPagination):
    pagination_class = PageNumberPagination
    page_size = 5 
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response("error", status=status.HTTP_401_Unauthorized) #unauthorized
        #유저 정보 불러오기
        user_info = User.objects.get(email=request.user)
        context = {
            "user": {
                "nickname": user_info.nickname,
                "age": user_info.age,
                "mbti": user_info.mbti,
                "gender": user_info.gender,
                "point": user_info.point,
            },
        }
        return Response(context)
    
    #마이페이지 수정 (개인정보 수정)
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 투표 시 poll_result 업데이트 함수 (uservote, nonuservote 둘 다)
# 어떤 poll에 choice_id번 선택지를 골랐음. + **extra_fields(Poll의 카테고리)의 정보가 있음.
import struct
def poll_result_update(poll_id, choice_number, **extra_fields):
    # user, nonUser 정보 처리는 위에서 해주면 좋겠다.
    # M, W \x00\x00\x00\x10 \x00\x00\x00\x10
    # E I S N T F P J \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 
    # 10 20_1 20_2 30_1 30_2 40 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10 \x00\x00\x00\x10
    poll_result, created = Poll_Result.objects.get_or_create(poll_id=poll_id)
    # 기존 값 가져오기 -> 나누고 정수 변환 -> 1 더하기 -> 비트로 변환하고 붙이기 -> 저장
    # 기존 값 가져오기
    poll_result.total_count += 1 #total_count 1 더해주기 
    #####
    poll = Poll.objects.get(id=poll_id)
    Poll.objects.filter(pk=poll_id).update(total_count = poll.total_count + 1)

    ######임시 함수 -->PollDetailView 함수에 추후에 이동 ######
    serialized_poll = PollSerializer(poll).data
    choices = serialized_poll.get('choices', [])
    poll_result.choice_count= len(choices)
    poll_result.save()
    #########################################################


    choice_set = getattr(poll_result, 'choice' + str(choice_number))
    # 나누고 정수 변환 -> 이 부분이 load 함수 역할. 괜히 함수 호출하면 시간 걸릴까봐 그냥 안에 넣었음. calcstat에서도 그대로 쓰면 됨.
    tmp_set = {}
    category_set = ["M", "W", "E", "I", "S", "N", "T", "F", "P", "J", "10", "20_1", "20_2", "30_1", "30_2", "40"]
    for i, key in enumerate(category_set):
        tmp_set[key] = int.from_bytes(choice_set[0 + 4 * i : 4 + 4 * i], byteorder='big', signed=False)
    # 1 더하기
    gender = extra_fields.get('gender')
    mbti = extra_fields.get('mbti')
    age = extra_fields.get('age')
    if gender:
        tmp_set[gender] += 1
    else :
        tmp_set['M'] += 1
        
    if mbti:
        for i in range(4):
            tmp_set[mbti[i]] += 1
    if age:
        tmp_set[age] += 1
    # 비트로 변환하고 붙이기
    res = bytearray()
    for i, key in enumerate(category_set):
        res += struct.pack('>i', tmp_set[key])
    # 저장
    setattr(poll_result, 'choice' + str(choice_number), res)
    poll_result.save()
    return None

def poll_result_remove(poll_id, choice_number, **extra_fields):
    poll = Poll.objects.get(id=poll_id)
    poll_result = Poll_Result.objects.get(poll=poll_id)
    # 기존 값 가져오기 -> 나누고 정수 변환 -> 1 더하기 -> 비트로 변환하고 붙이기 -> 저장
    # 기존 값 가져오기
    poll_result.total_count -= 1 #total_count 1 빼주기
    Poll.objects.filter(pk=poll_id).update(total_count = poll.total_count -1)

    ######임시 함수 -->PollDetailView 함수에 추후에 이동 ######
    serialized_poll = PollSerializer(poll).data
    choices = serialized_poll.get('choices', [])
    poll_result.choice_count= len(choices)
    poll_result.save()
    #########################################################

    choice_set = getattr(poll_result, 'choice' + str(choice_number))
    # 나누고 정수 변환 -> 이 부분이 load 함수 역할. 괜히 함수 호출하면 시간 걸릴까봐 그냥 안에 넣었음. calcstat에서도 그대로 쓰면 됨.
    tmp_set = {}
    category_set = ["M", "W", "E", "I", "S", "N", "T", "F", "P", "J", "10", "20_1", "20_2", "30_1", "30_2", "40"]
    for i, key in enumerate(category_set):
        tmp_set[key] = int.from_bytes(choice_set[0 + 4 * i : 4 + 4 * i], byteorder='big', signed=False)
    # 1 더하기
    gender = extra_fields.get('gender')
    mbti = extra_fields.get('mbti')
    age = extra_fields.get('age')
    if gender:
        tmp_set[gender] -= 1
    if mbti:
        for i in range(4):
            tmp_set[mbti[i]] -= 1
    if age:
        tmp_set[age] -= 1
    # 비트로 변환하고 붙이기
    res = bytearray()
    for i, key in enumerate(category_set):
        res += struct.pack('>i', tmp_set[key])
    # 저장
    setattr(poll_result, 'choice' + str(choice_number), res)
    poll_result.save()
    return None

class poll_result_page(APIView):
    def get(self, request, poll_id): #새로고침, 링크로 접속 시
        #기본 투표 정보
        poll = get_object_or_404(Poll, id=poll_id)
        statistics = poll_calcstat(poll_id)
        serialized_poll = PollSerializer(poll, context={'request': request}).data

        serialized_choice= False
        user = request.user
        if user.is_authenticated and user.voted_polls.filter(id=poll_id).exists():
            uservote = UserVote.objects.get(poll_id=poll_id, user=user)
            choice = Choice.objects.get(id = uservote.choice_id)
            serialized_choice = ChoiceSerializer(choice, many=False).data

        choice_dict= {}
        for idx, choice in enumerate(poll.choices.all()):
            choice_dict[idx] = str(choice)
        

        next_polls = Poll.objects.filter(id__gt =poll.id).order_by('id')[0:2][::-1]
        previous_polls = Poll.objects.filter(id__lt =poll.id).order_by('-id')[0:2]
        latest_polls = list(chain(next_polls, [poll], previous_polls))
        serialized_latest_polls = PollSerializer(latest_polls, many=True, context={'request': request}).data

        context = {
            "poll": serialized_poll,
            "choices": choice_dict,
            "statistics": statistics,
            "choice":serialized_choice,
            "latest_polls":serialized_latest_polls,
            }
        return Response(context)

    def post(self, request, poll_id): #투표 완료 버튼 후 
        #client에서 받은 정보 처리 
        received_data = request.data
        choice_id = received_data['choice_id'] #고유 id값
        choice_number = received_data['choice_number'] #해당 poll의 몇 번째 답변
        category_list = received_data['category_list']
        user=request.user

        #기본 투표 정보
        poll = get_object_or_404(Poll, id=poll_id)
        choice_dict= {}
        for idx, choice in enumerate(poll.choices.all()):
            choice_dict[idx] = str(choice)

        #포인트 업데이트
        if user.is_authenticated and user.voted_polls.filter(id=poll_id).exists():
            pass
        elif user.is_authenticated : 
            owner= User.objects.get(id= poll.owner.id)
            if user != owner : 
                User.objects.filter(id= poll.owner.id).update(point = owner.point + 10)
        else :
            owner= User.objects.get(id= poll.owner.id)
            User.objects.filter(id= poll.owner.id).update(point = owner.point + 1)

        #이미 투표 하였을 경우, poll_result_remove
        if user.is_authenticated and user.voted_polls.filter(id=poll_id).exists():
            uservote = UserVote.objects.get(poll_id=poll_id, user=user)
            prev_choice = uservote.choice.choice_number
            poll_result_remove(poll_id, prev_choice, **{'gender': uservote.gender, 'mbti': uservote.mbti, 'age': uservote.age})
            uservote.choice_id = choice_id
            uservote.age = user.age
            uservote.mbti = user.mbti
            uservote.gender = user.gender
            uservote.save()

        #user 정보 업데이트
        if user.is_authenticated and not user.voted_polls.filter(id=poll_id).exists():
            for category in category_list:
                setattr(user, category, received_data[category])
                user.save()

        #uservote 생성
        if user.is_authenticated and not user.voted_polls.filter(id=poll_id).exists():
            UserVote.objects.create(user =user, poll_id=poll_id, choice_id = choice_id, gender = user.gender, mbti = user.mbti, age = user.age)
            user.voted_polls.add(poll_id)


        #poll_result_update
        if user.is_authenticated:
            poll_result_update(poll_id, choice_number, **{'gender': user.gender, 'mbti': user.mbti, 'age': user.age})
        else:
            extra_fields = {}
            for i in category_list:
                extra_fields[i] = received_data[i]
                print(i)
                print(received_data[i])
            poll_result_update(poll_id, choice_number, **extra_fields)

        #statistics
        statistics = poll_calcstat(poll_id)
        
        if user.is_authenticated and user.voted_polls.filter(id=poll_id).exists():
            uservote = UserVote.objects.get(poll_id=poll_id, user=user)
            choice = Choice.objects.get(id = uservote.choice_id)


        serialized_choice = ChoiceSerializer(choice, many=False).data
        serialized_poll = PollSerializer(poll, context={'request': request}).data

        context = {
            "poll": serialized_poll,
            "choices": choice_dict,
            "statistics": statistics,
            "choice":serialized_choice,
            }
        return Response(context)


# 결과페이지 회원/비회원 투표 통계 계산 함수
def poll_calcstat(poll_id):
    poll_result, created = Poll_Result.objects.get_or_create(poll_id=poll_id)
    
    category_set = ["M", "W", "E", "I", "S", "N", "T", "F", "P", "J", "10", "20_1", "20_2", "30_1", "30_2", "40"]
    total_count = poll_result.total_count
    choice_count = poll_result.choice_count
    TOLERANCE = 0
    p = float(10**TOLERANCE)
    data_set = [[0 for _ in range(16)] for _ in range(choice_count)]
    sum = [0 for i in range(16)]

    result = {"gender":{"M":{}, "W":{}}, "mbti":{"E":{}, "I":{}, "S":{}, "N":{}, "T":{}, "F":{}, "P":{}, "J":{}}, "age":{"10":{}, "20_1":{}, "20_2":{}, "30_1":{}, "30_2":{}, "40":{}}, "choice":{}}
    for choice_id in range(choice_count):
        choice_set = getattr(poll_result, 'choice' + str(choice_id + 1))
        for i in range(16):
            n = int.from_bytes(choice_set[0 + 4 * i : 4 + 4 * i], byteorder='big', signed=False)
            data_set[choice_id][i] = n
            sum[i] += n
        result['choice']['choice' + str(choice_id + 1)] = int(((data_set[choice_id][0] + data_set[choice_id][1]) / total_count * 100) * p + 0.5) / p

    for i in range(2):
        for choice_id in range(choice_count):
            value = 0
            if sum[i] != 0:
                n = data_set[choice_id][i] / sum[i] * 100
                value = int(n * p + 0.5)/p
            result['gender'][category_set[i]]['choice' + str(choice_id + 1)] = value

    for i in range(2, 10):
        for choice_id in range(choice_count):
            value = 0
            if sum[i] != 0:
                n = data_set[choice_id][i] / sum[i] * 100
                value = int(n * p + 0.5)/p
            result['mbti'][category_set[i]]['choice' + str(choice_id + 1)] = value

    for i in range(10,16):
        for choice_id in range(choice_count):
            value = 0
            if sum[i] != 0:
                n = data_set[choice_id][i] / sum[i] * 100
                value = int(n * p + 0.5)/p
            result['age'][category_set[i]]['choice' + str(choice_id + 1)] = value
    result['total_count'] = total_count
    result['choice_count'] = choice_count
    return result


#포춘 쿠키 뽑기 함수
def get_random_fortune(mbti):
    default_fortune = "일시적인 오류입니다! 다음에 시도해주세요."
    selected_fortunes = fortunes.get(mbti, [])
    fortune = random.choice(selected_fortunes) if selected_fortunes else default_fortune
    if mbti != 'nonuser':
        fortune = mbti + '인 당신! ' + fortune
    return fortune

#포춘 쿠키 페이지 
@api_view(['POST'])    
def fortune(request):
    user = request.user
    if user.is_authenticated:
        random_fortune = get_random_fortune(user.mbti)
    else:
        random_fortune = get_random_fortune('nonuser')
    return Response({"random_fortune": random_fortune})

