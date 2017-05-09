from __future__ import absolute_import

import sys

import pytest
from django.test import RequestFactory

from django_cas_ng import backends

@pytest.mark.django_db
def test_backend_authentication_creating_a_user(monkeypatch, django_user_model):
    """
    Test the case where CAS authentication is creating a new user.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    backend = backends.CASBackend()
    user = backend.authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is not None
    assert user.username == 'test@example.com'
    assert django_user_model.objects.filter(
        username='test@example.com',
    ).exists()


def test_backend_authentication_do_not_create_user(monkeypatch, django_user_model, settings):
    """
    Test the case where CAS authentication is creating a new user.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    settings.CAS_CREATE_USER = False
    backend = backends.CASBackend()
    user = backend.authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is None
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()


@pytest.mark.django_db
def test_backend_for_existing_user(monkeypatch, django_user_model):
    """
    Test the case where CAS authenticates an existing user.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    existing_user = django_user_model.objects.create_user('test@example.com', '')

    backend = backends.CASBackend()
    user = backend.authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is not None
    assert user.username == 'test@example.com'
    assert user == existing_user


@pytest.mark.django_db
def test_backend_for_existing_user(monkeypatch, django_user_model):
    """
    Test the case where CAS authenticates an existing user, but request argument is None.
    """
    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    existing_user = django_user_model.objects.create_user('test@example.com', '')

    backend = backends.CASBackend()
    user = backend.authenticate(
        None, ticket='fake-ticket', service='fake-service',
    )

    assert user is not None
    assert user.username == 'test@example.com'
    assert user == existing_user


@pytest.mark.django_db
def test_backend_for_failed_auth(monkeypatch, django_user_model):
    """
    Test CAS authentication failure.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return None, {}, None

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    backend = backends.CASBackend()
    user = backend.authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is None
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()


@pytest.mark.django_db
def test_backend_user_can_authenticate(monkeypatch, django_user_model):
    """
    Test CAS authentication failure.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'ticket': ticket, 'service': service}, None

    # we mock out the verify method so that we can bypass the external http
    # calls needed for real authentication since we are testing the logic
    # around authentication.
    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    user = backends.CASBackend().authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is not None

    class AllowNoneBackend(backends.CASBackend):
        def user_can_authenticate(self, user):
            return False

    user = AllowNoneBackend().authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is None


@pytest.mark.django_db
def test_backend_does_not_apply_attributes_by_default(monkeypatch):
    """
    Test to make sure attributes returned from the provider are not assigned to
    the User model by default.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'is_staff': True, 'is_superuser': False}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    backend = backends.CASBackend()
    user = backend.authenticate(request, ticket='fake-ticket',
                                service='fake-service')

    assert user is not None
    assert not user.is_staff


@pytest.mark.django_db
def test_backend_applies_attributes_when_set(monkeypatch, settings):
    """
    If CAS_APPLY_ATTRIBUTES_TO_USER is set, make sure the attributes returned
    with the ticket are added to the User model.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'is_staff': True, 'is_superuser': False}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    settings.CAS_APPLY_ATTRIBUTES_TO_USER = True
    backend = backends.CASBackend()
    user = backend.authenticate(request, ticket='fake-ticket',
                                service='fake-service')

    assert user is not None
    assert user.is_staff
