from django.urls import path
from . import views

app_name = "vote"

urlpatterns = [
    # 공통
    path("", views.MainViewSet.as_view({'get': 'list'}), name="main"),
    
    path('search/', views.MainViewSearch.as_view(), name='search'),
    
    path("<int:poll_id>", views.PollDetailView.as_view(), name="detail"),
    path("<int:poll_id>/poll_result_page", views.poll_result_page.as_view(), name="poll_result_page"),
    # path("<int:poll_id>/gender", views.poll_classifyuser, name="poll_classifyuser"),
    # path(
    #     "<int:poll_id>/poll_result_page/<int:uservote_id>/<int:nonuservote_id>",
    #     views.poll_result_page,
    #     name="poll_result_page" ,
    # ),
    # 유저
    path("create", views.poll_create, name="poll_create"), #투표 만들기
    path("<int:poll_id>/like", views.PollLikeView.as_view(), name="poll_like"),
    path("<int:comment_id>/comment_like", views.CommentLikeView.as_view(), name="comment_like"),
    path("<int:poll_id>/comment", views.CommentView.as_view(), name="comment"),
    path("comment/<int:comment_id>/delete", views.comment_delete, name="comment_delete"),
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