from django.urls import path
from . import views

app_name = "vote"

urlpatterns = [
    # 공통
    path("", views.MainViewSet.as_view({'get': 'list'}), name="main"),
    path("event/", views.event, name="event"),
    path('search/', views.MainViewSearch.as_view(), name='search'),
    path("<int:poll_id>", views.PollDetailView.as_view(), name="detail"),
    path("<int:poll_id>/poll_result_page", views.poll_result_page.as_view(), name="poll_result_page"),
    #댓글 보이기
    path("<int:poll_id>/comment/<str:sort>", views.CommentView.as_view(), name="comment"),
    #댓글 쓰기
    path("<int:poll_id>/comment", views.comment_create, name="comment_create"),
    # 유저
    path("create", views.poll_create, name="poll_create"), #투표 만들기
    path("<int:poll_id>/like", views.PollLikeView.as_view(), name="poll_like"),
    path("<int:poll_id>/report", views.poll_report, name="poll_report"),
    path("<int:comment_id>/comment_like", views.CommentLikeView.as_view(), name="comment_like"),
    path("comment/<int:comment_id>/comment_report", views.comment_report, name="comment_report"),
    path("comment/<int:comment_id>/delete", views.comment_delete, name="comment_delete"),
    #마이페이지
    path("mypage_uservote", views.MypageUserVoteView.as_view(), name="mypage_uservote"),
    path("mypage_my_poll", views.MypageMyPollView.as_view(), name="mypage_uservote"),
    path("mypage_poll_like", views.MypagePollLikeView.as_view(), name="mypage_uservote"),
    path("mypage", views.MypageView.as_view(), name="mypage"),

    # path('get_replies/<int:comment_id>/', views.get_replies_view, name='get_replies'),    # 논유저
    # path('<int:poll_id>/<int:nonuservote_id>', views.poll_nonusergender, name='nonusergender'),
    # path(
    #     "<int:poll_id>/<int:nonuservote_id>/mbti",
    #     views.poll_nonusermbti,
    #     name="nonusermbti",
    # ),
    # path(
    #     "<int:poll_id>/<int:nonuservote_id>/1/1",
    #     views.poll_nonuserfinal,
    #     name="nonuserfinal",
    # ),
    path(
        "fortune/",
        views.fortune,
        name="fortune",
    ),
]