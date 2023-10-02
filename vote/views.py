import json
import random
import numpy as np
from .models import *
from accounts.models import *
from .fortunes import fortunes
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .serializers import *

# 메인페이지
class MainView(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_authenticated and user.custom_active == False:
            authentication_url = reverse("vs_account:email_verification", args=[user.id])
            return redirect(authentication_url)
        if user.is_authenticated:
            if user.gender == "" or user.mbti == "":
                return redirect("vote:update")
        
        polls = Poll.objects.all()
        polls = polls.order_by("-id")
        sort = request.GET.get("sort")
        promotion_polls = Poll.objects.filter(active=True).order_by("-views_count")[:3]

        if sort == "popular":
            polls = polls.order_by("-views_count")  # 인기순
        elif sort == "latest":
            polls = polls.order_by("-id")  # 최신순
        elif sort == "oldest":
            polls = polls.order_by("id")  # 등록순

        page = request.GET.get("page")
        random_poll = random.choice(polls) if polls.exists() else None
        paginator = Paginator(polls, 4)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            page_obj = paginator.page(page)

        polls = Poll.objects.all()

        if polls:
            today_poll = polls.last()
        else:
            today_poll = None
        
        phrases = [
            "투표하는 즐거움",
            "나의 투표를 가치있게",
            "나의 취향을 분석적으로",
            "mbti와 통계를 통한 투표 겨루기"
        ]

        random_phrase = random.choice(phrases)

        # Serialize the data
        serialized_polls = PollSerializer(polls, many=True).data

        response_data = {
            "polls": serialized_polls,
            "page_obj": page_obj.number,
            "paginator": {
                "num_pages": paginator.num_pages,
                "count": paginator.count,
            },
            "promotion_polls": PollSerializer(promotion_polls, many=True).data,
            "today_poll": PollSerializer(today_poll).data if today_poll else None,
            "random_phrase": random_phrase
        }

        return Response(response_data)

# 투표 디테일 페이지
class PollDetailView(APIView):
    def get(self, request, poll_id):
        user = request.user

        if user.is_authenticated and user.custom_active == False:
            authentication_url = reverse("vs_account:email_verification", args=[user.id])
            return redirect(authentication_url)

        if user.is_authenticated and (user.gender == "" or user.mbti == ""):
            return redirect("vote:update")

        poll = get_object_or_404(Poll, id=poll_id)

        if user.is_authenticated and user.voted_polls.filter(id=poll_id).exists():
            uservote = UserVote.objects.filter(poll_id=poll_id).get(user=user)
            calcstat_url = reverse("vote:calcstat", args=[poll_id, uservote.id, 0])
            return redirect(calcstat_url)
        else:
            poll.increase_views()  # 게시글 조회 수 증가
            loop_count = poll.choice_set.count()
            loop_time = list(range(0, loop_count))
            # Serialize the Poll object using PollSerializer
            serialized_poll = PollSerializer(poll).data
            context = {
                "poll": serialized_poll,
                "loop_time": loop_time,
            }
            return Response(context)


# 투표 게시글 좋아요 초기 검사
def get_like_status(request, poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
    except Poll.DoesNotExist:
        return JsonResponse({"error": "해당 투표가 존재하지 않습니다."}, status=404)

    user = request.user
    user_likes_poll = False

    if request.user.is_authenticated:
        if poll.poll_like.filter(id=user.id).exists():
            user_likes_poll = True

    context = {"user_likes_poll": user_likes_poll}
    return JsonResponse(context)


@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
def poll_like(request):
    serializer = PollLikeSerializer(data=request.data)
    
    if serializer.is_valid():
        poll_id = serializer.validated_data['poll_id']
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response({"error": "해당 투표가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if poll.poll_like.filter(id=user.id).exists():
            poll.poll_like.remove(user)
            message = "좋아요 취소"
            user_likes_poll = False
        else:
            poll.poll_like.add(user)
            message = "좋아요"
            user_likes_poll = True

        like_count = poll.poll_like.count()
        context = {
            "like_count": like_count,
            "message": message,
            "user_likes_poll": user_likes_poll,
        }
        return Response(context)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 댓글 좋아요
@login_required
def comment_like(request):
    user= request.user
    if user.is_authenticated and user.custom_active==False:
        authentication_url = reverse("vs_account:email_verification", args=[user.id])
        return redirect(authentication_url)
    if user.is_authenticated :
        if user.gender== "" or user.mbti=="":
            return redirect("vote:update")
    if request.method == "POST":
        req = json.loads(request.body)
        comment_id = req["comment_id"]

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"error": "해당 댓글이 존재하지 않습니다."}, status=404)

        user = request.user
        user_likes_comment = False
        
        if request.user.is_authenticated:
            user_id = user.id
            user_likes_comment = User.objects.get(id=user_id).comment_like.filter(id=comment.id).exists()

            if user_likes_comment:
                comment.comment_like.remove(user)
                message = "좋아요 취소"
            else:
                comment.comment_like.add(user)
                message = "좋아요"

            like_count = comment.comment_like.count()
            context = {
                "like_count": like_count,
                "message": message,
                "user_likes_comment": not user_likes_comment,
            }
            return JsonResponse(context)
        return redirect("/")


class MypageView(APIView):
    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "인증되지 않은 사용자입니다."}, status=401)

        if user.is_authenticated and user.custom_active == False:
            authentication_url = reverse("vs_account:email_verification", args=[user.id])
            return redirect(authentication_url)

        if user.is_authenticated:
            if user.gender == "" or user.mbti == "":
                return redirect("vote:update")

        # 사용자의 투표 목록 가져오기
        uservotes = UserVote.objects.filter(user=request.user)

        # 투표 목록을 페이지별로 페이징
        paginator = Paginator(uservotes, 4)
        page = request.GET.get("page")

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            page_obj = paginator.page(page)

        # 사용자가 좋아하는 투표 목록 가져오기
        polls_like = Poll.objects.filter(poll_like=request.user)
        length_polls_like = len(polls_like)

        # 페이지 객체를 시리얼라이즈
        serializer = PollSerializer(page_obj, many=True)

        context = {
            "uservotes": serializer.data,
            "polls_like": length_polls_like,
            "page_obj": page_obj.number,
            "num_pages": paginator.num_pages,
        }

        return Response(context)

    def put(self, request):
        user = request.user
        if user.is_authenticated and not user.custom_active:
            authentication_url = reverse("vs_account:email_verification", args=[user.id])
            return redirect(authentication_url)

        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 댓글 쓰기
@login_required
def comment_write_view(request, poll_id):
    user= request.user
    if user.is_authenticated and user.custom_active==False:
        authentication_url = reverse("vs_account:email_verification", args=[user.id])
        return redirect(authentication_url)
    if user.is_authenticated :
        if user.gender== "" or user.mbti=="":
            return redirect("vote:update")
    poll = get_object_or_404(Poll, id=poll_id)
    user_info = request.user  # 현재 로그인한 사용자
    content = request.POST.get("content")
    parent_comment_id = request.POST.get("parent_comment_id")
    
    try:
        user_vote = UserVote.objects.get(user=request.user, poll=poll)  # uservote에서 선택지 불러옴
        choice_text = user_vote.choice.choice_text

    except UserVote.DoesNotExist:
            user_vote = None
            choice_text = ""  # 또는 다른 기본값 설정
            
    if content:
        if parent_comment_id:  # 대댓글인 경우
            parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
            comment = Comment.objects.create(
                poll=poll,
                content=content,
                user_info=user_info,
                parent_comment=parent_comment,
                
            )
            parent_comment_data = {
                "nickname": parent_comment.user_info.nickname,
                "mbti": parent_comment.user_info.mbti,
                "gender": parent_comment.user_info.gender,
                "content": parent_comment.content,
                "created_at": parent_comment.created_at.strftime("%Y년 %m월 %d일"),
                "comment_id": parent_comment.pk,
            }
        else:  # 일반 댓글인 경우
            comment = Comment.objects.create(
                poll=poll,
                content=content,
                user_info=user_info,
            )
            parent_comment_data = None
        comments = Comment.objects.filter(poll_id=poll_id)
        poll.comments = comments.count()
        poll.save()
        comment_id =Comment.objects.last().pk
        data = {
            "nickname": user_info.nickname,
            "mbti": user_info.mbti,
            "gender": user_info.gender,
            "content": content,
            "created_at": comment.created_at.strftime("%Y년 %m월 %d일"),
            "comment_id": comment_id,
            "choice": choice_text,
            "new_comment_count": poll.comments,
        }
        
        comment.choice = user_vote.choice
        comment.save()
        if parent_comment_data:
            data["parent_comment"] = parent_comment_data

        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json"
        )


# 댓글 삭제
@login_required
def comment_delete_view(request, pk):
    user= request.user
    if user.is_authenticated and user.custom_active==False:
        authentication_url = reverse("vs_account:email_verification", args=[user.id])
        return redirect(authentication_url)
    if user.is_authenticated :
        if user.gender== "" or user.mbti=="":
            return redirect("vote:update")
    poll = get_object_or_404(Poll, id=pk)
    comment_id = request.POST.get("comment_id")
    target_comment = Comment.objects.get(pk=comment_id)
    if request.user == target_comment.user_info:
        target_comment.delete()
        comments = Comment.objects.filter(poll_id=pk)
        poll.comments = comments.count()
        poll.save()
        data = {"comment_id": comment_id, "success": True,
                "new_comment_count": poll.comments,}
    else:
        data = {"success": False, "error": "본인 댓글이 아닙니다."}
    return HttpResponse(
        json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json"
    )


# 대댓글 수 파악
def calculate_nested_count(request, comment_id):
    user= request.user
    if user.is_authenticated and user.custom_active==False:
        authentication_url = reverse("vs_account:email_verification", args=[user.id])
        return redirect(authentication_url)
    if user.is_authenticated :
        if user.gender== "" or user.mbti=="":
            return redirect("vote:update")
    nested_count = Comment.objects.filter(parent_comment_id=comment_id).count()
    return JsonResponse({"nested_count": nested_count})


# 투표 시 회원, 비회원 구분 (회원일시 바로 결과페이지, 비회원일시 성별 페이지)
@api_view(['POST'])
def poll_classifyuser(request, poll_id):
    user = request.user
    # if user.is_authenticated and user.custom_active==False:
    #     authentication_url = reverse("vs_account:email_verification", args=[user.id])
    #     return redirect(authentication_url)
    # if user.is_authenticated :
    #     if user.gender== "" or user.mbti=="":
    #         return redirect("vote:update")
    if request.method == "POST":
        poll = get_object_or_404(Poll, pk=poll_id)
        choice_id = request.POST.get("choice")
        choice = Choice.objects.get(id=choice_id)
        try: 
            uservote = UserVote(user=request.user, poll=poll, choice=choice) 
                # user = requqest.user에서 성공시 uservote, error 시 nonuservote
            uservote.save()
            user.voted_polls.add(poll_id)
                #user의 투표 리스트에 추가 
            poll_result_update(poll_id,uservote.choice_id, user.gender, user.mbti)

            # poll_result.total += 1
            # if user.gender == "M":
            #     poll_result.choice1_man += (
            #         1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #     )
            #     poll_result.choice2_man += (
            #         1 if int(choice_id) == 2 * (poll_id) else 0
            #     )
            # elif user.gender == "W":
            #     poll_result.choice1_woman += (
            #         1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #     )
            #     poll_result.choice2_woman += (
            #         1 if int(choice_id) == 2 * (poll_id) else 0
            #     )
            # for letter in user.mbti:
            #     if letter == "E":
            #         poll_result.choice1_E += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_E += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "I":
            #         poll_result.choice1_I += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_I += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "S":
            #         poll_result.choice1_S += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_S += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "N":
            #         poll_result.choice1_N += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_N += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "T":
            #         poll_result.choice1_T += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_T += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "F":
            #         poll_result.choice1_F += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_F += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "J":
            #         poll_result.choice1_J += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_J += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            #     elif letter == "P":
            #         poll_result.choice1_P += (
            #             1 if int(choice_id) == 2 * (poll_id) - 1 else 0
            #         )
            #         poll_result.choice2_P += (
            #             1 if int(choice_id) == 2 * (poll_id) else 0
            #         )
            # poll_result.save()
            poll_result_page__url = reverse("vote:poll_result_page", args=[poll_id, uservote.id, 0])
            return redirect(poll_result_page__url)
        except ValueError:
            #nonuservote 
            nonuservote = NonUserVote(poll=poll, choice=choice)
            #nonuservote 생성 mbti와 성별은 아직 받지 않았음.
            nonuservote.save()
            serialized_poll = PollSerializer(poll).data
            context = {
                "poll": serialized_poll,
                "gender": ["M", "W"],
                "nonuservote_id": nonuservote.id,
                #"loop_time": [0,1],
            }
            return Response(context)
    else:
        return redirect("/")


# 비회원 투표시 Gender update 후 mbti 페이지
@api_view(['POST'])
def poll_nonusermbti(request, poll_id, nonuservote_id):
    if request.method == "POST":
        choice_id = request.POST.get("choice")
        if choice_id == "M":
            NonUserVote.objects.filter(pk=nonuservote_id).update(gender="M")
        if choice_id == "W":
            NonUserVote.objects.filter(pk=nonuservote_id).update(gender="W")
        poll = get_object_or_404(Poll, pk=poll_id)
        serialized_poll = PollSerializer(poll).data
        context = {
            "poll": serialized_poll,
            "nonuservote_id": nonuservote_id,
        }
        return Response(context)
    else:
        return redirect("/")


# 비회원 투표시 투표 정보 전송 페이지
@api_view(['POST'])
def poll_nonuserfinal(request, poll_id, nonuservote_id):
    if request.method == "POST":
        selected_mbti = request.POST.get("selected_mbti")
        NonUserVote.objects.filter(pk=nonuservote_id).update(MBTI=selected_mbti)
        nonuservote = NonUserVote.objects.get(id=nonuservote_id)
        poll_result_update(poll_id,nonuservote.choice_id, nonuservote.gender, nonuservote.MBTI)
       
        poll_result_page_url = reverse("vote:poll_result_page", args=[poll_id, 0, nonuservote_id])
        return redirect(poll_result_page_url)
    else:
        return redirect("/")


# 투표 시 poll_result 업데이트 함수 (uservote, nonuservote 둘 다)
def poll_result_update(poll_id, choice_id, gender, mbti):
    poll_result,created = Poll_Result.objects.get_or_create(poll_id=poll_id)
    poll_result.total += 1
    if gender == "M":
        poll_result.choice1_man += (
            1 if choice_id == 2 * (poll_id) - 1 else 0
        )
        poll_result.choice2_man += (
            1 if choice_id == 2 * (poll_id) else 0
        )
    elif gender == "W":
        poll_result.choice1_woman += (
            1 if choice_id == 2 * (poll_id) - 1 else 0
        )
        poll_result.choice2_woman += (
            1 if choice_id == 2 * (poll_id) else 0
        )
    for letter in mbti:
        if letter == "E":
            poll_result.choice1_E += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_E += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "I":
            poll_result.choice1_I += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_I += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "S":
            poll_result.choice1_S += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_S += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "N":
            poll_result.choice1_N += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_N += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "T":
            poll_result.choice1_T += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_T += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "F":
            poll_result.choice1_F += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_F += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "J":
            poll_result.choice1_J += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_J += (
                1 if choice_id == 2 * (poll_id) else 0
            )
        elif letter == "P":
            poll_result.choice1_P += (
                1 if choice_id == 2 * (poll_id) - 1 else 0
            )
            poll_result.choice2_P += (
                1 if choice_id == 2 * (poll_id) else 0
            )
    poll_result.save()
    return None


# 결과 페이지
@api_view(['GET'])
def poll_result_page(request, poll_id, uservote_id, nonuservote_id):
    # user= request.user
    # if user.is_authenticated and user.custom_active==False:
    #     authentication_url = reverse("vs_account:email_verification", args=[user.id])
    #     return redirect(authentication_url)
    # if user.is_authenticated :
    #     if user.gender== "" or user.mbti=="":
    #         return redirect("vote:update")
    poll = get_object_or_404(Poll, pk=poll_id)
    uservotes = UserVote.objects.filter(poll_id=poll_id)
    choices=Choice.objects.filter(poll_id=poll_id)
    choice1 = choices[0].choice_text
    choice2 = choices[1].choice_text


    # 댓글
    comments = Comment.objects.filter(poll_id=poll_id)
    poll.comments = comments.count()
    now = datetime.now()
    for comment in comments:
        time_difference = now - comment.created_at
        comment.time_difference = time_difference.total_seconds() / 3600  # 시간 단위로 변환하여 저장


    #댓글 필터링     
    choice_filter = request.GET.get("choice_filter") #choice1, choice2  
    sort = request.GET.get("sort") #최신순, 인기순
    
    if choice_filter == choice1:
        comments = Comment.objects.filter(poll_id=poll_id, choice__choice_text=choice1)
    elif choice_filter == choice2:
        comments = Comment.objects.filter(poll_id=poll_id, choice__choice_text=choice2)
        
    if sort == "likes":
        comments = comments.annotate(like_count=Count('comment_like')).order_by('like_count', 'created_at')
    elif sort == "latest":
        comments = comments.order_by('created_at')    

    if sort == "likes" and choice_filter == choice1:
        comments = comments.filter(choice__choice_text=choice1).annotate(like_count=Count('comment_like')).order_by('like_count', 'created_at')
    elif sort == "likes" and choice_filter == choice2:
        comments = comments.filter(choice__choice_text=choice2).annotate(like_count=Count('comment_like')).order_by('like_count', 'created_at')


    #통계 계산 (calcstat 함수 사용)
    (total_count,
    choice1_percentage, choice2_percentage, 
    choice1_man_percentage, choice2_man_percentage,
    choice1_woman_percentage, choice2_woman_percentage,
    e_choice1_percentage, e_choice2_percentage,
    i_choice1_percentage, i_choice2_percentage,
    n_choice1_percentage, n_choice2_percentage,
    s_choice1_percentage, s_choice2_percentage,
    t_choice1_percentage, t_choice2_percentage,
    f_choice1_percentage, f_choice2_percentage,
    p_choice1_percentage, p_choice2_percentage,
    j_choice1_percentage, j_choice2_percentage
    ) = poll_calcstat(poll_id)
    
    
    #통계 분석
    key, analysis = poll_analysis(uservote_id, nonuservote_id, poll_id,    
        choice1_man_percentage, choice2_man_percentage,
        choice1_woman_percentage, choice2_woman_percentage,
        e_choice1_percentage, e_choice2_percentage,
        i_choice1_percentage, i_choice2_percentage,
        n_choice1_percentage, n_choice2_percentage,
        s_choice1_percentage, s_choice2_percentage,
        t_choice1_percentage, t_choice2_percentage,
        f_choice1_percentage, f_choice2_percentage,
        p_choice1_percentage, p_choice2_percentage,
        j_choice1_percentage, j_choice2_percentage)
    
    
    #serializer, ctx 
    serialized_poll = PollSerializer(poll).data
    serialized_comments= CommentSerializer(comments, many=True).data
    serialized_choices=ChoiceSerializer(choices, many=True).data
    ctx = {
        "total_count": total_count,
        "choice1_percentage": choice1_percentage,
        "choice2_percentage": choice2_percentage,
        "choice1_man_percentage": choice1_man_percentage,
        "choice2_man_percentage": choice2_man_percentage,
        "choice1_woman_percentage": choice1_woman_percentage,
        "choice2_woman_percentage": choice2_woman_percentage,
        "e_choice1_percentage": e_choice1_percentage,
        "e_choice2_percentage": e_choice2_percentage,
        "i_choice1_percentage": i_choice1_percentage,
        "i_choice2_percentage": i_choice2_percentage,
        "s_choice1_percentage": s_choice1_percentage,
        "s_choice2_percentage": s_choice2_percentage,
        "n_choice1_percentage": n_choice1_percentage,
        "n_choice2_percentage": n_choice2_percentage,
        "t_choice1_percentage": t_choice1_percentage,
        "t_choice2_percentage": t_choice2_percentage,
        "f_choice1_percentage": f_choice1_percentage,
        "f_choice2_percentage": f_choice2_percentage,
        "p_choice1_percentage": p_choice1_percentage,
        "p_choice2_percentage": p_choice2_percentage,
        "j_choice1_percentage": j_choice1_percentage,
        "j_choice2_percentage": j_choice2_percentage,
        "poll": serialized_poll,
        "comments": serialized_comments,
        "comments_count":comments.count(),
        "uservotes": uservotes,
        "sort": sort,
        "key": key,
        "analysis" : analysis,
        "choices": serialized_choices,
        "choice_filter":choice_filter,
        "new_comment_count": poll.comments,
    }
    return Response(ctx)


# 결과페이지 회원/비회원 투표 통계 계산 함수
def poll_calcstat(poll_id):
    poll_result = Poll_Result.objects.get(poll_id=poll_id)

    total_count = poll_result.total

    choice1_percentage = int(np.round((poll_result.choice1_man + poll_result.choice1_woman) / total_count * 100))
    choice2_percentage = int(np.round((poll_result.choice2_man + poll_result.choice2_woman) / total_count * 100))

    choice1_man_percentage = (
        (
            np.round(
                poll_result.choice1_man
                / (poll_result.choice1_man + poll_result.choice2_man)
                * 100,
                1,
            )
        )
        if (poll_result.choice1_man + poll_result.choice2_man) != 0
        else 0
    )
    choice2_man_percentage =  (
        (
            np.round(
                poll_result.choice2_man
                / (poll_result.choice1_man + poll_result.choice2_man)
                * 100,
                1,
            )
        )
        if (poll_result.choice1_man + poll_result.choice2_man) != 0
        else 0
    )
    choice1_woman_percentage = (
        (
            np.round(
                poll_result.choice1_woman
                / (poll_result.choice1_woman + poll_result.choice2_woman)
                * 100,
                1,
            )
        )
        if (poll_result.choice1_woman + poll_result.choice2_woman) != 0
        else 0
    )
    choice2_woman_percentage = (
        (
            np.round(
                poll_result.choice2_woman
                / (poll_result.choice1_woman + poll_result.choice2_woman)
                * 100,
                1,
            )
        )
        if (poll_result.choice1_woman + poll_result.choice2_woman) != 0
        else 0
    )

    e_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_E
                / (poll_result.choice1_E + poll_result.choice2_E)
                * 100
            )
        )
        if (poll_result.choice1_E + poll_result.choice2_E) != 0
        else 0
    )
    e_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_E
                / (poll_result.choice1_E + poll_result.choice2_E)
                * 100
            )
        )
        if (poll_result.choice1_E + poll_result.choice2_E) != 0
        else 0
    )
    i_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_I
                / (poll_result.choice1_I + poll_result.choice2_I)
                * 100
            )
        )
        if (poll_result.choice1_I + poll_result.choice2_I) != 0
        else 0
    )
    i_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_I
                / (poll_result.choice1_I + poll_result.choice2_I)
                * 100
            )
        )
        if (poll_result.choice1_I + poll_result.choice2_I) != 0
        else 0
    )

    n_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_N
                / (poll_result.choice1_N + poll_result.choice2_N)
                * 100
            )
        )
        if (poll_result.choice1_N + poll_result.choice2_N) != 0
        else 0
    )
    n_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_N
                / (poll_result.choice1_N + poll_result.choice2_N)
                * 100
            )
        )
        if (poll_result.choice1_N + poll_result.choice2_N) != 0
        else 0
    )
    s_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_S
                / (poll_result.choice1_S + poll_result.choice2_S)
                * 100
            )
        )
        if (poll_result.choice1_S + poll_result.choice2_S) != 0
        else 0
    )
    s_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_S
                / (poll_result.choice1_S + poll_result.choice2_S)
                * 100
            )
        )
        if (poll_result.choice1_S + poll_result.choice2_S) != 0
        else 0
    )

    t_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_T
                / (poll_result.choice1_T + poll_result.choice2_T)
                * 100
            )
        )
        if (poll_result.choice1_T + poll_result.choice2_T) != 0
        else 0
    )
    t_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_T
                / (poll_result.choice1_T + poll_result.choice2_T)
                * 100
            )
        )
        if (poll_result.choice1_T + poll_result.choice2_T) != 0
        else 0
    )
    f_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_F
                / (poll_result.choice1_F + poll_result.choice2_F)
                * 100
            )
        )
        if (poll_result.choice1_F + poll_result.choice2_F) != 0
        else 0
    )
    f_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_F
                / (poll_result.choice1_F + poll_result.choice2_F)
                * 100
            )
        )
        if (poll_result.choice1_F + poll_result.choice2_F) != 0
        else 0
    )

    p_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_P
                / (poll_result.choice1_P + poll_result.choice2_P)
                * 100
            )
        )
        if (poll_result.choice1_P + poll_result.choice2_P) != 0
        else 0
    )
    p_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_P
                / (poll_result.choice1_P + poll_result.choice2_P)
                * 100
            )
        )
        if (poll_result.choice1_P + poll_result.choice2_P) != 0
        else 0
    )
    j_choice1_percentage = (
        (
            np.round(
                poll_result.choice1_J
                / (poll_result.choice1_J + poll_result.choice2_J)
                * 100
            )
        )
        if (poll_result.choice1_J + poll_result.choice2_J) != 0
        else 0
    )
    j_choice2_percentage = (
        (
            np.round(
                poll_result.choice2_J
                / (poll_result.choice1_J + poll_result.choice2_J)
                * 100
            )
        )
        if (poll_result.choice1_J + poll_result.choice2_J) != 0
        else 0
    )

    return (total_count,
        choice1_percentage, choice2_percentage, 
        choice1_man_percentage, choice2_man_percentage,
        choice1_woman_percentage, choice2_woman_percentage,
        e_choice1_percentage, e_choice2_percentage,
        i_choice1_percentage, i_choice2_percentage,
        n_choice1_percentage, n_choice2_percentage,
        s_choice1_percentage, s_choice2_percentage,
        t_choice1_percentage, t_choice2_percentage,
        f_choice1_percentage, f_choice2_percentage,
        p_choice1_percentage, p_choice2_percentage,
        j_choice1_percentage, j_choice2_percentage)


# 결과페이지 성향 분석 함수 
def poll_analysis(uservote_id, nonuservote_id, poll_id,    
        choice1_man_percentage, choice2_man_percentage,
        choice1_woman_percentage, choice2_woman_percentage,
        e_choice1_percentage, e_choice2_percentage,
        i_choice1_percentage, i_choice2_percentage,
        n_choice1_percentage, n_choice2_percentage,
        s_choice1_percentage, s_choice2_percentage,
        t_choice1_percentage, t_choice2_percentage,
        f_choice1_percentage, f_choice2_percentage,
        p_choice1_percentage, p_choice2_percentage,
        j_choice1_percentage, j_choice2_percentage):
    try:
        currentvote = UserVote.objects.get(id=uservote_id)
        currentuser = currentvote.user
        currentgender = currentuser.gender
        currentmbti = currentuser.mbti 
    except ObjectDoesNotExist:
        currentvote = NonUserVote.objects.get(id=nonuservote_id)
        currentgender = currentvote.gender
        currentmbti = currentvote.MBTI

    dict = {}
    if currentvote.choice.id == 2*poll_id - 1:
        if currentgender == "M":
            dict["남성"] = choice1_man_percentage
        elif currentgender == "W":
            dict["여성"] = choice1_woman_percentage
        for letter in currentmbti:
            if letter == "E":
                dict["E"] = e_choice1_percentage
            elif letter == "I":
                dict["I"] = i_choice1_percentage
            elif letter == "S":
                dict["S"] = s_choice1_percentage
            elif letter == "N":
                dict["N"] = n_choice1_percentage
            elif letter == "T":
                dict["T"] = t_choice1_percentage
            elif letter == "F":
                dict["F"] = f_choice1_percentage
            elif letter == "P":
                dict["P"] = p_choice1_percentage
            elif letter == "J":
                dict["J"] = j_choice1_percentage
    if currentvote.choice.id == 2*poll_id :
        if currentgender == "M":
            dict["남성"] = choice2_man_percentage
        elif currentgender == "W":
            dict["여성"] = choice2_woman_percentage
        for letter in currentmbti:
            if letter == "E":
                dict["E"] = e_choice2_percentage
            elif letter == "I":
                dict["I"] = i_choice2_percentage
            elif letter == "S":
                dict["S"] = s_choice2_percentage
            elif letter == "N":
                dict["N"] = n_choice2_percentage
            elif letter == "T":
                dict["T"] = t_choice2_percentage
            elif letter == "F":
                dict["F"] = f_choice2_percentage
            elif letter == "P":
                dict["P"] = p_choice2_percentage
            elif letter == "J":
                dict["J"] = j_choice2_percentage

    maximum_key = max(dict, key=dict.get)
    maximum_value = dict[max(dict, key=dict.get)]

    minimum_key = min(dict, key=dict.get)
    minimum_value = 100 - dict[min(dict, key=dict.get)]

    if minimum_value >= maximum_value:
        key = minimum_key
    else : 
        key = maximum_key

    if key == minimum_key: 
        analysis= "당신은 " + key + "이지만 " + key + "의 " + str(minimum_value) + "%와 다른 선택을 했습니다."
    elif key == maximum_key:
        analysis= "당신은 " + key + "이며 " + key + "의 " + str(maximum_value) + "%와 같은 선택을 했습니다."

    return key, analysis


#포춘 쿠키 뽑기 함수
def get_random_fortune(mbti):
    default_fortune = "일시적인 오류입니다! 다음에 시도해주세요."
    selected_fortunes = fortunes.get(mbti, [])
    return random.choice(selected_fortunes) if selected_fortunes else default_fortune


#포춘 쿠키 페이지 
@api_view(['GET'])    
def fortune(request):
    user = request.user
    if user.is_authenticated:
        random_fortune = get_random_fortune(user.mbti)
    else:
        random_fortune = get_random_fortune('nonuser')

    return Response({"random_fortune": random_fortune})


# class PollList(APIView):
    
#      def get(self, request): #리스트 보여줄 때
#         polls = Poll.objects.all()
        
#         serializer = PollSerializer(polls, many=True) #여러개의 객체
#         return Response(serializer.data)