"""CAS login/logout replacement views"""

from __future__ import unicode_literals

from django.utils.six.moves import urllib_parse

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages

__all__ = ['login', 'logout']

def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    service = protocol + host + request.path
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

    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        prefix = (('http://', 'https://')[request.is_secure()] +
                  request.get_host())
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def _login_url(service):
    """Generates CAS login URL"""

    params = {'service': service}
    if settings.CAS_RENEW:
        params.update({'renew': 'true'})
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urllib_parse.urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urllib_parse.urlencode(params)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urllib_parse.urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urllib_parse.urlencode({'url': protocol + host + next_page})
    return url


def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated():
        message = "You are logged in as %s." % request.user.username
        messages.success(request, message)
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')
    service = _service_url(request, next_page)
    if ticket:
        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service, request=request)
        if user is not None:
            auth.login(request, user)
            name = user.first_name or user.username
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

    from django.contrib.auth import logout
    logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        # This is in most cases pointless if not CAS_RENEW is set. The user will
        # simply be logged in again on next request requiring authorization.
        return HttpResponseRedirect(next_page)
