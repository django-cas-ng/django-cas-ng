import warnings
from typing import Optional, Union
from urllib import parse as urllib_parse

from cas import CASClient
from django.conf import settings as django_settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    REDIRECT_FIELD_NAME,
    SESSION_KEY,
    load_backend,
)
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest
from django.shortcuts import resolve_url


class RedirectException(Exception):
    """Signals that a redirect could not be handled."""
    pass


def get_protocol(request: HttpRequest) -> str:
    """Returns 'http' or 'https' for the request protocol"""
    if request.is_secure():
        return 'https'
    return 'http'


def get_redirect_url(request: HttpRequest) -> str:
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """

    next_ = request.GET.get(REDIRECT_FIELD_NAME)
    if not next_:
        redirect_url = resolve_url(django_settings.CAS_REDIRECT_URL)
        if django_settings.CAS_IGNORE_REFERER:
            next_ = redirect_url
        else:
            next_ = request.META.get('HTTP_REFERER', redirect_url)
        prefix = urllib_parse.urlunparse(
            (get_protocol(request), request.get_host(), '', '', '', ''),
        )
        if next_.startswith(prefix):
            next_ = next_[len(prefix):]
    return next_


def get_service_url(request: HttpRequest, redirect_to: Optional[str] = None) -> str:
    """Generates application django service URL for CAS"""
    if hasattr(django_settings, 'CAS_ROOT_PROXIED_AS') and django_settings.CAS_ROOT_PROXIED_AS:
        service = urllib_parse.urljoin(django_settings.CAS_ROOT_PROXIED_AS, request.path)
    else:
        if django_settings.CAS_FORCE_SSL_SERVICE_URL:
            protocol = 'https'
        else:
            protocol = get_protocol(request)
        host = request.get_host()
        service = urllib_parse.urlunparse(
            (protocol, host, request.path, '', '', ''),
        )
    if not django_settings.CAS_STORE_NEXT:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urllib_parse.urlencode({
            REDIRECT_FIELD_NAME: redirect_to or get_redirect_url(request)
        })
    return service


def get_cas_client(
    service_url: Optional[str] = None,
    request: Optional[HttpRequest] = None,
) -> CASClient:
    """
    initializes the CASClient according to
    the CAS_* settigs
    """
    # Handle CAS_SERVER_URL without protocol and hostname
    server_url = django_settings.CAS_SERVER_URL
    if server_url and request and server_url.startswith('/'):
        scheme = request.META.get("X-Forwarded-Proto", request.scheme)
        server_url = scheme + "://" + request.META['HTTP_HOST'] + server_url
    # assert server_url.startswith('http'), "settings.CAS_SERVER_URL invalid"

    if not django_settings.CAS_VERIFY_SSL_CERTIFICATE:
        warnings.warn(
            "`CAS_VERIFY_SSL_CERTIFICATE` is disabled, meaning that SSL certificates "
            "are not being verified by a certificate authority. This can expose your "
            "system to various attacks and should _never_ be disabled in a production "
            "environment."
        )

    kwargs = dict(
        service_url=service_url,
        version=django_settings.CAS_VERSION,
        server_url=server_url,
        extra_login_params=django_settings.CAS_EXTRA_LOGIN_PARAMS,
        renew=django_settings.CAS_RENEW,
        username_attribute=django_settings.CAS_USERNAME_ATTRIBUTE,
        proxy_callback=django_settings.CAS_PROXY_CALLBACK,
        verify_ssl_certificate=django_settings.CAS_VERIFY_SSL_CERTIFICATE
    )
    if django_settings.CAS_SESSION_FACTORY:
        kwargs['session'] = django_settings.CAS_SESSION_FACTORY()
    if django_settings.CAS_VERSION == 1:
        kwargs.pop('proxy_callback')

    return CASClient(**kwargs)


def get_user_from_session(session: SessionBase) -> Union[User, AnonymousUser]:
    """
    Get User object (or AnonymousUser() if not logged in) from session.
    """
    try:
        user_id = session[SESSION_KEY]
        backend_path = session[BACKEND_SESSION_KEY]
        backend = load_backend(backend_path)
        return backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        return AnonymousUser()
