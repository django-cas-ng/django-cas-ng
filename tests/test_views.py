from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from importlib import import_module

from django_cas_ng.models import SessionTicket, ProxyGrantingTicket
from django_cas_ng.views import login, logout, callback

import pytest
import django

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


# function takes a request and applies a middleware process
def process_request_for_middleware(request, middleware):
    middleware = middleware()
    middleware.process_request(request)


@pytest.mark.django_db
def test_login_post_logout(django_user_model, settings):
    """
    Test that when CAS authentication creates a user, the signal is called with
    `created = True`
    """
    settings.CAS_VERSION = 'CAS_2_SAML_1_0'

    data = {'logoutRequest': '<samlp:LogoutRequest '
                             'xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
                             '<samlp:SessionIndex>fake-ticket'
                             '</samlp:SessionIndex></samlp:LogoutRequest>'
            }
    session = SessionStore()
    session['fake_session'] = 'fake-session'
    session.save()
    assert SessionStore(session_key=session.session_key) is not None

    factory = RequestFactory()
    request = factory.post('/login/', data)
    request.session = session

    # Create a fake session ticket and make sure it exists in the db
    session_ticket = SessionTicket.objects.create(
        session_key=session.session_key,
        ticket='fake-ticket'
    )
    assert session_ticket is not None
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is True
    user = django_user_model.objects.create(username='test-user', email='test@example.com')
    assert user is not None
    assert django_user_model.objects.filter(username='test-user').exists() is True
    request.user = user

    # Create a fake pgt
    pgt = ProxyGrantingTicket.objects.create(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket')
    assert pgt is not None
    assert ProxyGrantingTicket.objects.filter(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket').exists() is True

    login(request)
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is False
    assert ProxyGrantingTicket.objects.filter(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket').exists() is False
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is False


@pytest.mark.django_db
def test_login_authenticate_and_create_user(monkeypatch, django_user_model, settings):
    """
    Test the case where the login view authenticates a new user.
    """
    # No need to test the message framework
    settings.CAS_LOGIN_MSG = None
    # Make sure we use our backend
    settings.AUTHENTICATION_BACKENDS = ['django_cas_ng.backends.CASBackend']
    # Json serializer was havinga  hard time
    settings.SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    factory = RequestFactory()
    request = factory.get('/login/', {'ticket': 'fake-ticket',
                                      'service': 'fake-service'})

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)

    response = login(request)
    assert response.status_code == 302
    assert response['Location'] == '/'
    if django.VERSION[0] < 2:
        assert django_user_model.objects.get(username='test@example.com').is_authenticated() is True
    else:
        assert django_user_model.objects.get(username='test@example.com').is_authenticated is True


@pytest.mark.django_db
def test_login_authenticate_do_not_create_user(monkeypatch, django_user_model, settings):
    """
    Test the case where the login view authenticates a user, but does not
    create a user based on the CAS_CREATE_USER setting.
    """
    # No need to test the message framework
    settings.CAS_CREATE_USER = False
    # No need to test the message framework
    settings.CAS_LOGIN_MSG = None
    # Make sure we use our backend
    settings.AUTHENTICATION_BACKENDS = ['django_cas_ng.backends.CASBackend']
    # Json serializer was havinga  hard time
    settings.SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    factory = RequestFactory()
    request = factory.get('/login/', {'ticket': 'fake-ticket',
                                      'service': 'fake-service'})

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)

    with pytest.raises(PermissionDenied):
        login(request)
    assert django_user_model.objects.filter(username='test@example.com').exists() is False


@pytest.mark.django_db
def test_login_proxy_callback(monkeypatch, django_user_model, settings):
    """
    Test the case where the login view has a pgtiou.
    """
    # No need to test the message framework
    settings.CAS_PROXY_CALLBACK = True
    # No need to test the message framework
    settings.CAS_LOGIN_MSG = None
    # Make sure we use our backend
    settings.AUTHENTICATION_BACKENDS = ['django_cas_ng.backends.CASBackend']
    # Json serializer was havinga  hard time
    settings.SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    factory = RequestFactory()
    request = factory.get('/login/', {'ticket': 'fake-ticket',
                                      'service': 'fake-service'})

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)
    request.session['pgtiou'] = 'fake-pgtiou'
    request.session.save()

    user = django_user_model.objects.create_user('test@example.com', '')
    assert user is not None
    pgt = ProxyGrantingTicket.objects.create(session_key=request.session.session_key,
                                             user=user, pgtiou='fake-pgtiou',
                                             pgt='fake-pgt')
    assert pgt is not None

    response = login(request)
    assert response.status_code == 302
    if django.VERSION[0] < 2:
        assert django_user_model.objects.get(username='test@example.com').is_authenticated() is True
    else:
        assert django_user_model.objects.get(username='test@example.com').is_authenticated is True
    assert ProxyGrantingTicket.objects.filter(pgtiou='fake-pgtiou').exists() is True
    assert ProxyGrantingTicket.objects.filter(pgtiou='fake-pgtiou').count() == 1


@pytest.mark.django_db
def test_login_redirect_based_on_cookie(monkeypatch, django_user_model, settings):
    """
    Test the case where the login view authenticates a new user and redirects them based on cookie.
    """
    # No need to test the message framework
    settings.CAS_LOGIN_MSG = None
    # Make sure we use our backend
    settings.AUTHENTICATION_BACKENDS = ['django_cas_ng.backends.CASBackend']
    # Json serializer was havinga  hard time
    settings.SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
    # Store next as cookie
    settings.CAS_STORE_NEXT = True

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    factory = RequestFactory()
    request = factory.get('/login/', {'ticket': 'fake-ticket',
                                      'service': 'fake-service'})

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)
    # Add the next pointer
    request.session['CASNEXT'] = '/admin/'

    response = login(request)
    assert response.status_code == 302
    assert response['Location'] == '/admin/'

    assert 'CASNEXT' not in request.session
    if django.VERSION[0] < 2:
        assert django_user_model.objects.get(username='test@example.com').is_authenticated() is True
    else:
        assert django_user_model.objects.get(username='test@example.com').is_authenticated is True


@pytest.mark.django_db
def test_login_no_ticket():
    """
    Test the case where we try to login with no ticket
    """
    factory = RequestFactory()
    request = factory.get('/login/')

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)

    response = login(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_no_ticket_stores_default_next(settings):
    """
    When there is no explicit next pointer, it gets stored in a cookie
    """
    settings.CAS_STORE_NEXT = True

    factory = RequestFactory()
    request = factory.get('/login/')

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)

    response = login(request)
    assert response.status_code == 302

    assert 'CASNEXT' in request.session
    assert request.session['CASNEXT'] == '/'


@pytest.mark.django_db
def test_login_no_ticket_stores_explicit_next(settings):
    """
    When there is an explicit next pointer, it gets stored in the cookie
    """
    settings.CAS_STORE_NEXT = True

    factory = RequestFactory()
    request = factory.get('/login/', {'next': '/admin/'})

    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)
    # Create a user object from middleware
    process_request_for_middleware(request, AuthenticationMiddleware)

    response = login(request)
    assert response.status_code == 302

    assert 'CASNEXT' in request.session
    assert request.session['CASNEXT'] == '/admin/'


def test_login_put_not_allowed():
    factory = RequestFactory()
    request = factory.put('/login/')
    response = login(request)
    assert response.status_code == 405


def test_login_delete_not_allowed():
    factory = RequestFactory()
    request = factory.delete('/login/')
    response = login(request)
    assert response.status_code == 405


@pytest.mark.django_db
def test_logout_not_completely(django_user_model, settings):
    """
    Test the case where the user logs out, without the logout_completely flag.
    """
    settings.CAS_LOGOUT_COMPLETELY = False

    factory = RequestFactory()
    request = factory.get('/logout/')
    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)

    user = django_user_model.objects.create_user('test@example.com', '')
    assert user is not None
    request.user = user

    response = logout(request)
    assert response.status_code == 302
    if django.VERSION[0] < 2:
        assert request.user.is_anonymous() is True
    else:
        assert request.user.is_anonymous is True


@pytest.mark.django_db
def test_logout_completely(django_user_model, settings):
    """
    Test the case where the user logs out.
    """
    settings.CAS_LOGOUT_COMPLETELY = True

    factory = RequestFactory()
    request = factory.get('/logout/')
    # Create a session object from the middleware
    process_request_for_middleware(request, SessionMiddleware)

    user = django_user_model.objects.create_user('test@example.com', '')
    assert user is not None
    request.user = user

    response = logout(request)
    assert response.status_code == 302
    if django.VERSION[0] < 2:
        assert request.user.is_anonymous() is True
    else:
        assert request.user.is_anonymous is True

def test_logout_post_not_allowed():
    factory = RequestFactory()
    request = factory.post('/logout/')
    response = logout(request)
    assert response.status_code == 405


def test_logout_put_not_allowed():
    factory = RequestFactory()
    request = factory.put('/logout/')
    response = logout(request)
    assert response.status_code == 405


def test_logout_delete_not_allowed():
    factory = RequestFactory()
    request = factory.delete('/logout/')
    response = logout(request)
    assert response.status_code == 405


@pytest.mark.django_db
def test_callback_create_pgt():
    """
    Test the case where a pgt callback is used.
    """
    factory = RequestFactory()
    request = factory.get('/callback/', {'pgtId': 'fake-pgtId',
                                         'pgtIou': 'fake-pgtIou'})

    response = callback(request)
    assert response.status_code == 200
    assert ProxyGrantingTicket.objects.filter(pgt='fake-pgtId',
                                              pgtiou='fake-pgtIou'
                                              ).exists() is True


@pytest.mark.django_db
def test_callback_post_logout(django_user_model, settings):
    """
    Test that when logout is from a callback
    """
    settings.CAS_VERSION = 'CAS_2_SAML_1_0'

    data = {'logoutRequest': '<samlp:LogoutRequest '
                             'xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
                             '<samlp:SessionIndex>fake-ticket'
                             '</samlp:SessionIndex></samlp:LogoutRequest>'
            }
    session = SessionStore()
    session['fake_session'] = 'fake-session'
    session.save()
    assert SessionStore(session_key=session.session_key) is not None

    factory = RequestFactory()
    request = factory.post('/callback/', data)
    request.session = session

    # Create a fake session ticket and make sure it exists in the db
    session_ticket = SessionTicket.objects.create(
        session_key=session.session_key,
        ticket='fake-ticket'
    )
    assert session_ticket is not None
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is True
    user = django_user_model.objects.create(username='test-user', email='test@example.com')
    assert user is not None
    assert django_user_model.objects.filter(username='test-user').exists() is True
    request.user = user

    # Create a fake pgt
    pgt = ProxyGrantingTicket.objects.create(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket')
    assert pgt is not None
    assert ProxyGrantingTicket.objects.filter(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket').exists() is True

    callback(request)
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is False
    assert ProxyGrantingTicket.objects.filter(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket').exists() is False
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is False


def test_callback_put_not_allowed():
    factory = RequestFactory()
    request = factory.put('/callback/')
    response = callback(request)
    assert response.status_code == 405


def test_callback_delete_not_allowed():
    factory = RequestFactory()
    request = factory.delete('/callback/')
    response = callback(request)
    assert response.status_code == 405
