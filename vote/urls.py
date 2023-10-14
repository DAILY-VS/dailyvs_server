from django.urls import path
from . import views

from rest_framework.urlpatterns import format_suffix_patterns #추가

app_name = "vote"

urlpatterns = [
    # 공통
    path("", views.MainView.as_view(), name="main"),
    path("<int:poll_id>/", views.PollDetailView.as_view(), name="detail"),
    path("<int:poll_id>/poll_result_page", views.poll_result_page.as_view(), name="poll_result_page"),
    # path("<int:poll_id>/gender", views.poll_classifyuser, name="poll_classifyuser"),
    # path(
    #     "<int:poll_id>/poll_result_page/<int:uservote_id>/<int:nonuservote_id>",
    #     views.poll_result_page,
    #     name="poll_result_page" ,
    # ),
    # 유저
    path("<int:poll_id>/like", views.PollLikeView.as_view(), name="poll_like"),
    path("comment_like/", views.CommentLikeView.as_view(), name="comment_like"),
    path("<int:poll_id>/comment", views.CommentView.as_view(), name="comment"),
    path("<int:poll_id>/comment/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("mypage/", views.MypageView.as_view(), name="mypage"),

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
    
    #path('api/', views.PollList.as_view(), name='api'),
]