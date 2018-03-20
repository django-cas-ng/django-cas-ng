from __future__ import absolute_import

import pytest
from django.test import RequestFactory
from django.core.exceptions import ImproperlyConfigured

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
    Test the case where CAS authentication is not creating a new user.
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
def test_backend_for_existing_user_no_request(monkeypatch, django_user_model):
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
        return 'test@example.com', {'is_staff': 'True', 'is_superuser': 'False'}, None

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
        return 'test@example.com', {'is_staff': 'True', 'is_superuser': 'False'}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    settings.CAS_APPLY_ATTRIBUTES_TO_USER = True
    backend = backends.CASBackend()
    user = backend.authenticate(request, ticket='fake-ticket',
                                service='fake-service')

    assert user is not None
    assert user.is_staff


@pytest.mark.django_db
def test_cas_attributes_renaming_working(monkeypatch, settings):
    """
    Test to make sure attributes are renamed according to the setting file
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', \
            {'ln': 'MyLastName','fn':'MyFirstName','unkownAttr':'knownAttr'}, \
            None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    settings.CAS_RENAME_ATTRIBUTES = {'ln':'last_name'}
    settings.CAS_APPLY_ATTRIBUTES_TO_USER = True

    backend = backends.CASBackend()
    user = backend.authenticate(request, ticket='fake-ticket',
                                service='fake-service')

    # Checking user data
    assert user is not None
    assert user.last_name == 'MyLastName'
    assert user.first_name == ''

    # checking session data
    session_attr = request.session['attributes']
    assert session_attr['fn'] == 'MyFirstName'
    assert session_attr['last_name'] == 'MyLastName'
    with pytest.raises(KeyError):
        session_attr['ln']  


@pytest.mark.django_db
def test_boolean_attributes_applied_as_booleans(monkeypatch, settings):
    """
    If CAS_CREATE_USER_WITH_ID is True and 'id' is in the attributes, use this
    field to get_or_create a User.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'is_staff': 'True', 'is_superuser': 'False'}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    settings.CAS_APPLY_ATTRIBUTES_TO_USER = True
    backend = backends.CASBackend()
    user = backend.authenticate(request, ticket='fake-ticket',
                                service='fake-service')

    assert user is not None
    assert user.is_superuser is False
    assert user.is_staff is True


@pytest.mark.django_db
def test_backend_authentication_creates_a_user_with_id_attribute(monkeypatch, django_user_model, settings):
    """
    If CAS_CREATE_USER_WITH_ID is True and 'id' is in the attributes, use this
    field to get_or_create a User.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'id': 999, 'is_staff': True, 'is_superuser': False}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    settings.CAS_CREATE_USER_WITH_ID = True
    backend = backends.CASBackend()
    user = backend.authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert user is not None
    assert user.username == 'test@example.com'
    assert django_user_model.objects.filter(id=999).exists()


@pytest.mark.django_db
def test_backend_authentication_create_user_with_id_and_user_exists(monkeypatch, django_user_model, settings):
    """
    If CAS_CREATE_USER_WITH_ID is True and and the User already exists, don't create another user.
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'id': 999, 'is_staff': True, 'is_superuser': False}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    existing_user = django_user_model.objects.create_user('test@example.com', '', id=999)

    settings.CAS_CREATE_USER_WITH_ID = True
    backend = backends.CASBackend()
    user = backend.authenticate(
        request, ticket='fake-ticket', service='fake-service',
    )

    assert django_user_model.objects.all().count() == 1
    assert user is not None
    assert user.username == 'test@example.com'
    assert user.id == 999
    assert user == existing_user


@pytest.mark.django_db
def test_backend_authentication_create_user_with_id_and_no_id_provided(monkeypatch, django_user_model, settings):
    """
    CAS_CREATE_USER_WITH_ID is True and the 'id' field is not in the attributes.

    Should raise ImproperlyConfigured exception
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', {'is_staff': True, 'is_superuser': False}, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    settings.CAS_CREATE_USER_WITH_ID = True
    backend = backends.CASBackend()
    with pytest.raises(ImproperlyConfigured) as excinfo:
        user = backend.authenticate(
            request, ticket='fake-ticket', service='fake-service',
        )

    assert "CAS_CREATE_USER_WITH_ID is True, but `'id'` is not part of attributes." in str(excinfo)


@pytest.mark.django_db
def test_backend_authentication_create_user_with_id_and_attributes(monkeypatch, django_user_model, settings):
    """
    CAS_CREATE_USER_WITH_ID is True and the attributes are not provided.

    Should raise ImproperlyConfigured exception
    """
    factory = RequestFactory()
    request = factory.get('/login/')
    request.session = {}

    def mock_verify(ticket, service):
        return 'test@example.com', None, None

    monkeypatch.setattr('cas.CASClientV2.verify_ticket', mock_verify)

    # sanity check
    assert not django_user_model.objects.filter(
        username='test@example.com',
    ).exists()

    settings.CAS_CREATE_USER_WITH_ID = True
    backend = backends.CASBackend()
    with pytest.raises(ImproperlyConfigured) as excinfo:
        user = backend.authenticate(
            request, ticket='fake-ticket', service='fake-service',
        )

    assert "CAS_CREATE_USER_WITH_ID is True, but no attributes were provided" in str(excinfo)
