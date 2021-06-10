"""CAS authentication middleware"""


from urllib import parse as urllib_parse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import LoginView as login, LogoutView as logout
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

from .views import LoginView as cas_login, LogoutView as cas_logout

__all__ = ["CASMiddleware"]


class CASMiddleware(MiddlewareMixin):
    """Middleware that allows CAS authentication on admin pages"""

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(error)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """

        if view_func == login:
            return cas_login(request, *view_args, **view_kwargs)

        if view_func == logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if view_func in (cas_login, cas_logout):
            return None

        if settings.CAS_ADMIN_REDIRECT:
            if settings.CAS_ADMIN_PREFIX:
                if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                    return None
            elif not view_func.__module__.startswith('django.contrib.admin.'):
                return None
        else:
            return None

        if view_func.__name__ == 'logout':
            return HttpResponseRedirect(reverse(settings.CAS_LOGOUT_URL_NAME))

        if request.user.is_authenticated:
            if request.user.is_staff:
                return None
            raise PermissionDenied(_('You do not have staff privileges.'))
        params = urllib_parse.urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
        return HttpResponseRedirect(reverse(settings.CAS_LOGIN_URL_NAME) + '?' + params)
