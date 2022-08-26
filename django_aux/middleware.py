from django.conf import settings
from django.shortcuts import redirect


class CheckPasswordChangeMiddleware:
    '''
        Middleware checks the user instance to see if a password change is required,
        if so it redirects to the password change path specificed in settings
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        fpc_attr = getattr(settings, 'FORCE_PASSWORD_CHANGE_ATTR', 'force_password_change')
        fpc = getattr(request.user, fpc_attr, False)
        is_auth = getattr(request.user,'is_authenticated', False)
        no_pmatch = request.path.rstrip('/') != settings.PASSWORD_CHANGE_URL.rstrip('/')
        if fpc and is_auth and no_pmatch:
            return redirect(settings.PASSWORD_CHANGE_URL)
        return self.get_response(request)