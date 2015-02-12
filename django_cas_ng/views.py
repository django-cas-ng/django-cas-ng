"""CAS login/logout replacement views"""

from __future__ import unicode_literals

from django.utils.six.moves import urllib_parse

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import (
    logout as auth_logout,
    login as auth_login,
    authenticate,
)
from django.contrib import messages

__all__ = ['login', 'logout']


def get_protocol(request):
    if request.is_secure():
        return 'https'
    else:
        return 'http'


def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    protocol = get_protocol(request)
    host = request.get_host()
    service = urllib_parse.urlunparse(
        (protocol, host, request.path, '', '', ''),
    )
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urllib_parse.urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """

    next_ = request.GET.get(REDIRECT_FIELD_NAME)
    if not next_:
        if settings.CAS_IGNORE_REFERER:
            next_ = settings.CAS_REDIRECT_URL
        else:
            next_ = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        prefix = urllib_parse.urlunparse(
            (get_protocol(request), request.get_host(), '', '', '', ''),
        )
        if next_.startswith(prefix):
            next_ = next_[len(prefix):]
    return next_


def _login_url(service):
    """Generates CAS login URL"""

    params = {'service': service}
    if settings.CAS_RENEW:
        params.update({'renew': 'true'})
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    url = urllib_parse.urljoin(settings.CAS_SERVER_URL, 'login')
    query = urllib_parse.urlencode(params)
    return url + '?' + query


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urllib_parse.urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = get_protocol(request)
        host = request.get_host()
        next_page_url = urllib_parse.urlunparse(
            (protocol, host, next_page, '', '', ''),
        )
        url += '?' + urllib_parse.urlencode({'url': next_page_url})
    return url


def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated():
        message = "You are logged in as %s." % request.user.get_username()
        messages.success(request, message)
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')
    service = _service_url(request, next_page)
    if ticket:
        user = authenticate(ticket=ticket, service=service, request=request)
        if user is not None:
            auth_login(request, user)
            name = user.get_username()
            message = "Login succeeded. Welcome, %s." % name
            messages.success(request, message)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(_login_url(service))
        else:
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""
    auth_logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        # This is in most cases pointless if not CAS_RENEW is set. The user will
        # simply be logged in again on next request requiring authorization.
        return HttpResponseRedirect(next_page)
