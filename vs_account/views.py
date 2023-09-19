# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import get_user_model
# from .forms import SignupForm
# from .forms import EmailForm
# from .forms import PasswordResetForm
# from django.contrib import auth
# from django.contrib.auth.forms import AuthenticationForm
# from .forms import *
# from vote.models import *
# from django.contrib.auth.forms import PasswordChangeForm
# from django.contrib.auth import update_session_auth_hash
# from django.views.generic.edit import DeleteView
# from django.urls import reverse_lazy
# from .models import User
# from django.urls import reverse


# import random
# import string
# from django.contrib.auth.decorators import login_required
# import smtplib

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str


# User = get_user_model()

# #회원가입
# def signup(request):
#     user= request.user
#     if user.is_authenticated and user.custom_active==False:
#         authentication_url = reverse("vs_account:email_verification", args=[user.id])
#         return redirect(authentication_url)
#     if user.is_authenticated :
#         if user.gender== "" or user.mbti=="":
#             return redirect("vote:update")
#     if request.method == "POST":
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.custom_active=False
#             user.save()
#             auth.login(request, user)
#             pk=str(user.pk)
#             return redirect(f'/account/email_verification/{user.pk}/')
#         else:
#             ctx = {
#                 "form": form,
#             }
#             return render(request, "account/signup.html", context=ctx)
#     else:
#         form = SignupForm()
#         ctx = {
#             "form": form,
#         }
#         return render(request, template_name="account/signup.html", context=ctx)
    
# #로그인
# def login(request):  
#     user= request.user
#     if user.is_authenticated and user.custom_active==False:
#         authentication_url = reverse("vs_account:email_verification", args=[user.id])
#         return redirect(authentication_url)
#     if user.is_authenticated :
#         if user.gender== "" or user.mbti=="":
#             return redirect("vote:update")
#     if request.method == "POST":
#         form = AuthenticationForm(request, request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             auth.login(request, user)
#             return redirect("/")
#         else:
#             wrong_password = True  # 비밀번호가 틀렸을 때 변수를 설정하여 템플릿으로 전달
#             context = {
#                 "form": form,
#                 "wrong_password": wrong_password,  # 변수를 템플릿으로 전달
#             }
#             return render(request, "account/login.html", context=context)
#     else:
#         form = AuthenticationForm()
#         context = {
#             "form": form,
#         }
#         return render(request, "account/login.html", context=context)

# #로그아웃
# def logout(request):  
#     auth.logout(request)
#     return redirect("/")

# #비밀번호 변경
# def change_password(request):
#     user= request.user
#     if user.is_authenticated and user.custom_active==False:
#         authentication_url = reverse("vs_account:email_verification", args=[user.id])
#         return redirect(authentication_url)
#     if user.is_authenticated :
#         if user.gender== "" or user.mbti=="":
#             return redirect("vote:update")
#     if request.method == "POST":
#         form = PasswordChangeForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # 변경 후 로그인 상태 유지
#             return redirect("vote:mypage")  # 변경 후 이동할 페이지
#     else:
#         form = PasswordChangeForm(request.user)
#     context = {"form": form}
#     return render(request, "account/change_password.html", context)

# #회원탈퇴
# class UserDeleteView(DeleteView):
#     model = User
#     template_name = "account/delete.html"
#     success_url = reverse_lazy("vote:mypage")
#     form_class = UserDeleteForm

#     def get_object(self, queryset=None):
#         return self.request.user
    
# #이메일 인증
# def generate_verification_code():
#     return ''.join(random.choices(string.digits, k=6))

# @login_required
# def email_verification(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     code = generate_verification_code()
#     print(code)
#     try:
#             smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
#             smtp_server.starttls()

#             EMAIL_HOST_USER = 'dailyvsofficial@gmail.com'
#             EMAIL_HOST_PASSWORD = 'qousltfgowhagxab'

#             smtp_server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

#             subject = 'Daily-VS 이메일 인증코드'
#             message = f'Daily-VS 이메일 인증코드는 다음과 같습니다. {code}'
#             sender_email = EMAIL_HOST_USER
#             recipient_email = user.email
#             msg = f'Subject: {subject}\n\n{message}'
#             smtp_server.sendmail(sender_email, recipient_email, msg.encode('utf-8'))

#     except smtplib.SMTPException as e:
#             print("An error occurred:", str(e))
#     finally:
#             smtp_server.quit()
#     return render(request, "account/email_verification.html", {"user": user, "code": code})

# def call(request):
#     code = request.POST.get('code')  # Get the code from the form submission
#     token = request.POST.get('token')
#     if token == code:
#             request.user.custom_active = True
#             request.user.save()
#             return redirect("/")  # Redirect to login page after successful verification
#     else:
#             return render(request, "account/verification_error.html")


# #비밀번호 찾기를 위한 이메일 입력 뷰
# def password_reset_input(request):
#     if request.method == "POST":
#         form = EmailForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             reset_url = request.build_absolute_uri('/account/password_reset_confirm')
#             try : 
#                 send_password_reset_email(email, reset_url)
#             except :
#                 return render(request, "account/password_reset_input.html", {"form": form, "text": "없는 이메일입니다."})
#             return render(request, "account/send_password_reset_email.html", {"email": email})
#     else:
#         form = EmailForm()
#     return render(request, "account/password_reset_input.html", {"form": form})

# #비밀번호 찾기를 위한 이메일 전송
# def send_password_reset_email(email, reset_url):
#     user = User.objects.get(email=email)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     token = default_token_generator.make_token(user)
#     reset_link = f"{reset_url}/{uid}/{token}/"
    
#     subject = 'Daily-VS 비밀번호 재설정'
#     message = f'비밀번호를 재설정하려면 아래 링크를 클릭하세요:\n\n{reset_link}'
#     sender_email = 'dailyvs@gmail.com'
#     recipient_email = user.email
#     msg = f'Subject: {subject}\n\n{message}'
    
#     try:
#         smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
#         smtp_server.starttls()

#         EMAIL_HOST_USER = 'dailyvsofficial@gmail.com'
#         EMAIL_HOST_PASSWORD = 'qousltfgowhagxab'

#         smtp_server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
#         smtp_server.sendmail(sender_email, recipient_email, msg.encode('utf-8'))

#     except smtplib.SMTPException as e:
#         print("An error occurred:", str(e))
#     finally:
#         smtp_server.quit()

# #비밀번호 찾기 후 재설정
# def password_reset_confirm(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
#     if user is not None and default_token_generator.check_token(user, token):
#         if request.method == "POST":
#             form = PasswordResetForm(request.POST)
#             if form.is_valid():
#                 new_password = form.cleaned_data['new_password']
#                 confirm_new_password = form.cleaned_data['confirm_new_password']
#                 if new_password == confirm_new_password : 
#                     print(124)
#                     user.set_password(new_password)
#                     user.save()
#                     return redirect("vs_account:login")  # 비밀번호 재설정 후 로그인 페이지로 이동
#                 else : 
#                     print(5)
#                     return render(request, "account/password_reset_confirm.html", {"uidb64": uidb64, "token": token, "text" : "비밀번호가 일치하지 않습니다.",'form' :form})
#         else:
#             print(3)
#             form = PasswordResetForm()
#             return render(request, "account/password_reset_confirm.html", {"uidb64": uidb64, "token": token, 'form' :form})
#     else:
#         print(6)
#         return render(request, "account/password_reset_error.html")