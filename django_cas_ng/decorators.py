"""Replacement authentication decorators that work around redirection loops"""


from functools import wraps
from typing import Callable, Optional, TypeVar

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http.response import HttpResponseBase
from urllib.parse import quote

__all__ = ['login_required', 'permission_required', 'user_passes_test']
# Retains the arguments and return type of original decorated function
# Decorated function must be a view, which returns HttpResponseBase
VIEW = TypeVar("VIEW", bound=Callable[..., HttpResponseBase])


def user_passes_test(test_func: Callable[[User], bool],
                     login_url: Optional[str] = None,
                     redirect_field_name: str = REDIRECT_FIELD_NAME) \
        -> Callable[[VIEW], VIEW]:
    """Replacement for django.contrib.auth.decorators.user_passes_test that
    returns 403 Forbidden if the user is already logged in.
    """

    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            if request.user.is_authenticated:
                raise PermissionDenied

            path = '%s?%s=%s' % (login_url, redirect_field_name,
                                 quote(request.get_full_path()))
            return HttpResponseRedirect(path)
        return wrapper
    return decorator


def permission_required(perm: str, login_url: Optional[str] = None) \
        -> Callable[[VIEW], VIEW]:
    """Replacement for django.contrib.auth.decorators.permission_required that
    returns 403 Forbidden if the user is already logged in.
    """

    return user_passes_test(lambda u: u.has_perm(perm), login_url=login_url)
