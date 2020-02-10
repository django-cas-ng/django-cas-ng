Custom Backends
===============

The ``CASBackend`` class is heavily inspired from Django's own
``RemoteUserBackend`` and allows for some configurability through subclassing.
If you need more control than django-cas-ng's settings provide. For instance,
here is an example backend that only allows some users to login through CAS:

..  code-block:: python

    from django_cas_ng.backends import CASBackend

    class MyCASBackend(CASBackend):
        def user_can_authenticate(self, user):
            if user.has_permission('can_cas_login'):
                return True
            return False

If you need more control over the authentication mechanism of your project than
django-cas-ng's settings provide, you can create your own authentication
backend that inherits from ``django_cas_ng.backends.CASBackend`` and override
these attributes or methods:

- CASBackend.clean_username(username)
- CASBackend.user_can_authenticate(user)
    Returns whether the user is allowed to authenticate. For consistency with
    Django's own behavior, django-cas-ng will allow all users to authenticate
    through CAS on Django versions lower than 1.10; starting with Django 1.10
    however, django-cas-ng will prevent users with ``is_active=False`` from
    authenticating.
    See also `django.contrib.auth.backends.RemoteUserBackend`_.
- CASBackend.configure_user(user)
- CASBackend.bad_attributes_reject(request, username, attributes)

.. _django.contrib.auth.backends.RemoteUserBackend: https://docs.djangoproject.com/en/3.0/ref/contrib/auth/#django.contrib.auth.backends.RemoteUserBackend

Example
-------

For example, to
accept a user belonging to departmentNumber 421 only, define in ``mysite/settings.py``
the key-value constant:

..  code-block:: python

    MY_ATTRIBUTE_CONTROL = ('departmentNumber', '421')

and the authentication backends:

..  code-block:: python

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'mysite.backends.MyCASBackend',
    ]

and create a file ``mysite/backends.py`` containing:

..  code-block:: python

    from django_cas_ng.backends import CASBackend
    from django.contrib import messages
    from django.conf import settings


    class MyCASBackend(CASBackend):
        def user_can_authenticate(self, user):
            return True

        def bad_attributes_reject(self, request, username, attributes):
            attribute = settings.MY_ATTRIBUTE_CONTROL[0]
            value = settings.MY_ATTRIBUTE_CONTROL[1]

            if attribute not in attributes:
                message = 'No \''+ attribute + '\' in SAML attributes'
                messages.add_message(request, messages.ERROR, message)
                return message

            if value not in attributes[attribute]:
                message = 'User ' + str(username) + ' is not in ' + value + ' ' + attribute + ', should be one of ' + str(attributes[attribute])
                messages.add_message(request, messages.ERROR, message)
                return message

            return None

CASBackend API Reference
------------------------

.. autoclass:: django_cas_ng.backends.CASBackend
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
