from django.http import HttpResponseForbidden
from django.utils.functional import SimpleLazyObject
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django.shortcuts import redirect


class SuperUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if not self._is_admin_api_authenticated(request):
            return redirect("/error")
        response = self.get_response(request)
        return response
    
    def _is_admin_api_authenticated(self, request) -> bool:
        user = request.user
        request.user = SimpleLazyObject(lambda: self._get_token_user(request, user))
        is_admin_api: bool = request.path_info.startswith("/api/")
        is_not_admin: bool = not request.user.is_superuser
        return False if (is_admin_api and is_not_admin) else True

    @staticmethod
    def _get_token_user(request, user):
        try:
            authenticator = JWTCookieAuthenticationn()
            user, token_obj = authenticator.authenticate(request)
            return user
        except Exception:
            return user

class DisableCSRFMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
