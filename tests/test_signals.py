from __future__ import absolute_import
import pytest

from django.test import RequestFactory
from django.dispatch import receiver

from django_cas_ng.backends import CASBackend
from django_cas_ng.signals import cas_user_authenticated


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
        return 'test@example.com', {'ticket': ticket, 'service': service}

    callback_values = {}

    @receiver(cas_user_authenticated)
    def callback(sender, **kwargs):
        callback_values.update(kwargs)

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('django_cas_ng.backends._verify', mock_verify)

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
        return 'test@example.com', {'ticket': ticket, 'service': service}

    callback_values = {}

    @receiver(cas_user_authenticated)
    def callback(sender, **kwargs):
        callback_values.update(kwargs)

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('django_cas_ng.backends._verify', mock_verify)

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
        return None, {}

    callback_values = {}

    @receiver(cas_user_authenticated)
    def callback(sender, **kwargs):
        callback_values.update(kwargs)

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('django_cas_ng.backends._verify', mock_verify)

    # sanity check
    backend = CASBackend()
    user = backend.authenticate(
        ticket='fake-ticket', service='fake-service', request=request,
    )

    assert user is None
    assert callback_values == {}
