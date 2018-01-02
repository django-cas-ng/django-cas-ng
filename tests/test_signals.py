from __future__ import absolute_import
import pytest

from django.conf import settings
from django.test import RequestFactory
from django.dispatch import receiver
from importlib import import_module

from django_cas_ng.models import SessionTicket
from django_cas_ng.backends import CASBackend
from django_cas_ng.signals import cas_user_authenticated, cas_user_logout
from django_cas_ng.views import login, logout

import django

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


@pytest.mark.django_db
def test_signal_when_user_logout_manual(monkeypatch, django_user_model):
    session = SessionStore()
    session['fake_session_key'] = 'fake-session_value'
    session.save()
    assert SessionStore(session_key=session.session_key) is not None

    factory = RequestFactory()
    request = factory.get('/logout')
    request.session = session

    # Create a fake session ticket and make sure it exists in the db
    session_ticket = SessionTicket.objects.create(
        session_key=session.session_key,
        ticket='fake-ticket'
    )

    user = django_user_model.objects.create_user('test@example.com', '')
    assert user is not None
    request.user = user

    callback_values = {}

    @receiver(cas_user_logout)
    def callback(sender, session, **kwargs):
        callback_values.update(kwargs)
        callback_values['session'] = dict(session)

    response = logout(request)
    if django.VERSION[0] < 2:
        assert request.user.is_anonymous() is True
    else:
        assert request.user.is_anonymous is True
    assert 'user' in callback_values
    assert callback_values['user'] == user
    assert 'session' in callback_values
    assert callback_values['session'].get('fake_session_key') == 'fake-session_value'
    assert 'ticket' in callback_values
    assert callback_values['ticket'] == 'fake-ticket'


@pytest.mark.django_db
def test_signal_when_user_logout_slo(monkeypatch, django_user_model, settings):
    data = {'logoutRequest': '<samlp:LogoutRequest '
                             'xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
                             '<samlp:SessionIndex>fake-ticket'
                             '</samlp:SessionIndex></samlp:LogoutRequest>'
           }

    settings.CAS_VERSION = 'CAS_2_SAML_1_0'

    factory = RequestFactory()
    request = factory.post('/login', data)
    # user session and current requests.session are different
    request.session = {}

    user = django_user_model.objects.create_user('test@example.com', '')
    assert user is not None


    session = SessionStore()
    session['fake_session_key'] = 'fake-session_value'
    session.save()
    assert SessionStore(session_key=session.session_key) is not None

    # Create a fake session ticket and make sure it exists in the db
    session_ticket = SessionTicket.objects.create(
        session_key=session.session_key,
        ticket='fake-ticket'
    )

    callback_values = {}

    @receiver(cas_user_logout)
    def callback(sender, session, **kwargs):
        callback_values.update(kwargs)
        callback_values['session'] = dict(session)


    response = login(request)
    assert 'user' in callback_values
    assert 'session' in callback_values
    assert callback_values['session'].get('fake_session_key') == 'fake-session_value'
    assert 'ticket' in callback_values
    assert callback_values['ticket'] == 'fake-ticket'



@pytest.mark.django_db
def test_signal_when_user_is_created(monkeypatch, django_user_model):
    """
    Test that when CAS authentication creates a user, the signal is called with
    `created = True`
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    callback_values = {}

    @receiver(cas_user_authenticated)
    def callback(sender, **kwargs):
        callback_values.update(kwargs)

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    backend = CASBackend()
    user = backend.authenticate(
        ticket='fake-ticket', service='fake-service', request=request,
    )

    assert 'user' in callback_values
    assert callback_values.get('user') == user
    assert callback_values.get('created') == True
    assert 'attributes' in callback_values
    assert 'ticket' in callback_values
    assert 'service' in callback_values


@pytest.mark.django_db
def test_signal_when_user_already_exists(monkeypatch, django_user_model):
    """
    Test that when CAS authentication creates a user, the signal is called with
    `created = False`
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    callback_values = {}

    @receiver(cas_user_authenticated)
    def callback(sender, **kwargs):
        callback_values.update(kwargs)

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    existing_user = django_user_model.objects.create_user(
        'test@example.com', '',
    )

    backend = CASBackend()
    user = backend.authenticate(
        ticket='fake-ticket', service='fake-service', request=request,
    )

    assert 'user' in callback_values
    assert callback_values.get('user') == user == existing_user
    assert callback_values.get('created') == False
    assert 'attributes' in callback_values
    assert 'ticket' in callback_values
    assert 'service' in callback_values


@pytest.mark.django_db
def test_signal_not_fired_if_auth_fails(monkeypatch, django_user_model):
    """
    Test that the cas_user_authenticated signal is not fired when CAS
    authentication fails.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return None, {}, None

    callback_values = {}

    @receiver(cas_user_authenticated)
    def callback(sender, **kwargs):
        callback_values.update(kwargs)

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    backend = CASBackend()
    user = backend.authenticate(
        ticket='fake-ticket', service='fake-service', request=request,
    )

    assert user is None
    assert callback_values == {}
