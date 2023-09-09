from django.urls import path
from . import views

app_name = "vs_account"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("change_password/", views.change_password, name="change_password"),
    path("delete/", views.UserDeleteView.as_view(), name="delete"),
    path("email_verification/<int:user_id>/", views.email_verification, name="email_verification"),
    path('call/', views.call, name='call'),
    path("password_reset_input/", views.password_reset_input, name="password_reset_input"),
    path("send_password_reset_email/", views.send_password_reset_email, name="send_password_reset_email"),
    path("password_reset_confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    ]

