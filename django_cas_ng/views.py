"""CAS login/logout replacement views"""


from datetime import timedelta
from importlib import import_module
from typing import Any
from urllib import parse as urllib_parse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import SESSION_KEY_MAXLENGTH, ProxyGrantingTicket, SessionTicket
from .signals import cas_user_logout
from .utils import (
    RedirectException,
    get_cas_client,
    get_protocol,
    get_redirect_url,
    get_service_url,
    get_user_from_session,
)

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

__all__ = ['LoginView', 'LogoutView', 'CallbackView']


def clean_next_page(request, next_page):
    if not next_page:
        return next_page
    if settings.CAS_CHECK_NEXT and not is_local_url(request.build_absolute_uri('/'), next_page):
        raise RedirectException("Non-local url is forbidden to be redirected to.")
    return next_page


def is_local_url(host_url, url):
    """
    :param host_url: is an absolute host url, say https://site.com/
    :param url: is any url
    :return: Is :url: local to :host_url:?
    """
    url = url.strip()
    parsed_url = urllib_parse.urlparse(url)
    if not parsed_url.netloc:
        return True
    parsed_host = urllib_parse.urlparse(host_url)
    if parsed_url.netloc != parsed_host.netloc:
        return False
    if parsed_url.scheme != parsed_host.scheme and parsed_url.scheme:
        return False
    url_path = parsed_url.path if parsed_url.path.endswith('/') else parsed_url.path + '/'
    host_path = parsed_host.path if parsed_host.path.endswith('/') else parsed_host.path + '/'
    return url_path.startswith(host_path)


class LoginView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def successful_login(self, request: HttpRequest, next_page: str) -> HttpResponse:
        """
        This method is called on successful login. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).

        :param request:
        :param next_page:
        :return:
        """
        return HttpResponseRedirect(next_page)

    def post(self, request: HttpRequest) -> HttpResponse:
        next_page = clean_next_page(request, request.POST.get('next', settings.CAS_REDIRECT_URL))
        service_url = get_service_url(request, next_page)
        client = get_cas_client(service_url=service_url, request=request)

        if request.POST.get('logoutRequest'):
            clean_sessions(client, request)
            return HttpResponseRedirect(next_page)

        return HttpResponseRedirect(client.get_login_url())

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Forwards to CAS login URL or verifies CAS ticket

        :param request:
        :return:
        """
        next_page = clean_next_page(request, request.GET.get('next'))
        required = request.GET.get('required', False)

        service_url = get_service_url(request, next_page)
        client = get_cas_client(service_url=service_url, request=request)

        if not next_page and settings.CAS_STORE_NEXT and 'CASNEXT' in request.session:
            next_page = request.session['CASNEXT']
            request.session['CASNEXT'] = None

        if not next_page:
            next_page = get_redirect_url(request)

        if request.user.is_authenticated:
            if settings.CAS_LOGGED_MSG is not None:
                message = settings.CAS_LOGGED_MSG % request.user.get_username()
                messages.success(request, message)
            return self.successful_login(request=request, next_page=next_page)

        ticket = request.GET.get('ticket')
        if not ticket:
            if settings.CAS_STORE_NEXT:
                request.session['CASNEXT'] = next_page
            return HttpResponseRedirect(client.get_login_url())

        user = authenticate(ticket=ticket,
                            service=service_url,
                            request=request)
        pgtiou = request.session.get("pgtiou")
        if user is not None:
            auth_login(request, user)

            # from https://code.djangoproject.com/ticket/19147
            if not request.session.session_key:
                request.session.save()

            # Truncate session key to a max of its value length.
            # When using the signed_cookies session backend, the
            # session key can potentially be longer than this.
            session_key = request.session.session_key[:SESSION_KEY_MAXLENGTH]

            if not request.session.exists(session_key):
                request.session.create()

            try:
                st = SessionTicket.objects.get(session_key=session_key)
                st.ticket = ticket
                st.save()
            except SessionTicket.DoesNotExist:
                SessionTicket.objects.create(
                    session_key=session_key,
                    ticket=ticket
                )

            if pgtiou and settings.CAS_PROXY_CALLBACK:
                # Delete old PGT
                ProxyGrantingTicket.objects.filter(
                    user=user,
                    session_key=session_key
                ).delete()
                # Set new PGT ticket
                try:
                    pgt = ProxyGrantingTicket.objects.get(pgtiou=pgtiou)
                    pgt.user = user
                    pgt.session_key = session_key
                    pgt.save()
                except ProxyGrantingTicket.DoesNotExist:
                    pass

            if settings.CAS_LOGIN_MSG is not None:
                name = user.get_username()
                message = settings.CAS_LOGIN_MSG % name
                messages.success(request, message)

            return self.successful_login(request=request, next_page=next_page)

        if settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(client.get_login_url())

        raise PermissionDenied(_('Login failed.'))


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Redirects to CAS logout page

        :param request:
        :return:
        """
        next_page = clean_next_page(request, request.GET.get('next'))

        # try to find the ticket matching current session for logout signal

        # Truncate session key to a max of its value length
        # When using the signed_cookies session backend, the
        # session key can potentially be longer than this.
        session_key = None
        if request.session and request.session.session_key:
            session_key = request.session.session_key[:SESSION_KEY_MAXLENGTH]

        try:
            st = SessionTicket.objects.get(session_key=session_key)
            ticket = st.ticket
        except SessionTicket.DoesNotExist:
            ticket = None
        # send logout signal
        cas_user_logout.send(
            sender="manual",
            user=request.user,
            session=request.session,
            ticket=ticket,
        )

        # clean current session ProxyGrantingTicket and SessionTicket
        ProxyGrantingTicket.objects.filter(session_key=session_key).delete()
        SessionTicket.objects.filter(session_key=session_key).delete()
        auth_logout(request)

        next_page = next_page or get_redirect_url(request)
        if settings.CAS_LOGOUT_COMPLETELY:
            if hasattr(settings, 'CAS_ROOT_PROXIED_AS') and settings.CAS_ROOT_PROXIED_AS:
                protocol, host, _, _, _, _ = urllib_parse.urlparse(settings.CAS_ROOT_PROXIED_AS)
            else:
                protocol = get_protocol(request)
                host = request.get_host()
            redirect_url = urllib_parse.urlunparse(
                (protocol, host, next_page, '', '', ''),
            )
            client = get_cas_client(request=request)
            return HttpResponseRedirect(client.get_logout_url(redirect_url))

        # This is in most cases pointless if not CAS_RENEW is set. The user will
        # simply be logged in again on next request requiring authorization.
        return HttpResponseRedirect(next_page)


class CallbackView(View):
    """
    Read PGT and PGTIOU sent by CAS
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.POST.get('logoutRequest'):
            clean_sessions(get_cas_client(request=request), request)
            return HttpResponse("{}\n".format(_('ok')), content_type="text/plain")

        return HttpResponseBadRequest('Missing logoutRequest')

    def get(self, request: HttpRequest) -> HttpResponse:
        pgtid = request.GET.get('pgtId')
        pgtiou = request.GET.get('pgtIou')

        pgt = ProxyGrantingTicket.objects.create(pgtiou=pgtiou, pgt=pgtid)
        pgt.save()

        ProxyGrantingTicket.objects.filter(
            session_key=None,
            date__lt=(timezone.now() - timedelta(seconds=60))
        ).delete()

        return HttpResponse("{}\n".format(_('ok')), content_type="text/plain")


def clean_sessions(client, request):
    if not hasattr(client, 'get_saml_slos'):
        return

    for slo in client.get_saml_slos(request.POST.get('logoutRequest')):
        try:
            st = SessionTicket.objects.get(ticket=slo.text)
            session = SessionStore(session_key=st.session_key)
            # send logout signal
            cas_user_logout.send(
                sender="slo",
                user=get_user_from_session(session),
                session=session,
                ticket=slo.text,
            )
            session.flush()
            # clean logout session ProxyGrantingTicket and SessionTicket
            ProxyGrantingTicket.objects.filter(session_key=st.session_key).delete()
            SessionTicket.objects.filter(session_key=st.session_key).delete()
        except SessionTicket.DoesNotExist:
            pass
