from django.urls import path
from . import views
from vote.views import *
from rest_framework.urlpatterns import format_suffix_patterns #추가

app_name = "vote"

urlpatterns = [
    # 공통
    path("", views.main, name="main"),
    path("<int:poll_id>/", views.poll_detail, name="detail"),
    path("<int:poll_id>/gender", views.classifyuser, name="classifyuser"),
    path(
        "<int:poll_id>/calcstat/<int:uservote_id>/<int:nonuservote_id>",
        views.calcstat,
        name="calcstat",
    ),
    # 유저
    path("like/", views.poll_like, name="like"),
     path("comment_like/", views.comment_like, name="comment_like"),
    path(
        "get-like-status/<int:poll_id>/", views.get_like_status, name="get_like_status"
    ),
    path("mypage/", views.mypage, name="mypage"),
    path("mypage/update/", views.mypage_update, name="update"),
    path(
        "<int:poll_id>/comment/write/", views.comment_write_view, name="comment_write"
    ),
    path("<int:pk>/comment/delete/", views.comment_delete_view, name="comment_delete"),
    path(
        "calculate-nested-count/<int:comment_id>/",
        views.calculate_nested_count,
        name="calculate_nested_count",
    ),
    # path('get_replies/<int:comment_id>/', views.get_replies_view, name='get_replies'),    # 논유저
    # path('<int:poll_id>/<int:nonuservote_id>', views.poll_nonusergender, name='nonusergender'),
    path(
        "<int:poll_id>/<int:nonuservote_id>/mbti",
        views.poll_nonusermbti,
        name="nonusermbti",
    ),
    path(
        "<int:poll_id>/<int:nonuservote_id>/1/1",
        views.poll_nonuserfinal,
        name="nonuserfinal",
    ),
    path(
        "fortune/",
        views.fortune,
        name="fortune",
    ),
    
    path('api/', PollList.as_view(), name='api'),
]