from __future__ import absolute_import
from django.test import TestCase
import re
from django.contrib.auth import get_user_model

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.http import HttpResponseRedirect
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from accounts.models import UserManager, User

from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC,
)
class ConfirmationViewTests(TestCase):

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=False, ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN=10
    )
    def test_email_verification_mandatory(self):
        c = Client()
        resp = c.post(
            reverse("rest_register"),
            {
                "email": "john@example.com",
                "password1": "qkrtlsqls12**",
                "password2": "qkrtlsqls12**",
                "nickname": "asdf",
                "gender": "M",
                "mbti": "ISTP",
                "age": "10"
            },
            follow=True,
        )
        # User.objects.create(email="john@example.com", password="qkrtlsqls12**",nickname="asdf",gender="M",mbti="ISTP",age="10")
        print(EmailAddress.objects.all())
        new_user = EmailAddress.objects.get(email="john@example.com")
        print(new_user)
        new_user.verified = True
        new_user.save()
        print(User.objects.all())