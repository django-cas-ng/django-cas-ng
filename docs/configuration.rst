Configuration
-------------

.. contents:: Table of Contents
   :depth: 3

In order for your project to use ``django-cas-ng``, you'll need to configure
certain settings, add URL mappings, and sync your database.

Here is a post on `guide to create a demo integration project <https://djangocas.dev/blog/django-cas-ng-example-project/>`_.

You can also try `live demo <https://django-cas-ng-demo.herokuapp.com/>`_.

Settings
^^^^^^^^

Now add it to the middleware, authentication backends and installed apps in your settings.
Make sure you also have the authentication middleware installed.
Here's an example:

..  code-block:: python

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_cas_ng',
        ...
    )

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django_cas_ng.middleware.CASMiddleware',
        ...
    )

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )

Set the following required setting in ``settings.py``:


``CAS_SERVER_URL`` [Required]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the only setting you must explicitly define.
Set it to the base URL of your CAS source (e.g. https://account.example.com/cas/).


``CAS_ADMIN_REDIRECT`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``True``, django-cas-ng will also take over the Django administration site.
If you use a mix of CAS accounts and local Django accounts, and want to use
the latter to log in to the administration site, you should set it to ``False``.

The default is ``True``.


``CAS_ADMIN_PREFIX`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The URL prefix of the Django administration site.
If undefined, the CAS middleware will check the view being rendered to
see if it lives in ``django.contrib.admin.views``.

If ``CAS_ADMIN_REDIRECT`` is ``False``, this option will be ignored.

The default is ``None``.


``CAS_CREATE_USER`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a user when the CAS authentication is successful.

The default is ``True``.


``CAS_CREATE_USER_WITH_ID`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a user using the ``id`` field provided by
the attributes returned by the CAS provider. Raises
``ImproperlyConfigured`` exception if attributes are not provided or do not
contain the field ``id``.

The default is ``False``.


``CAS_LOGIN_MSG`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Welcome message send via the messages framework upon
successful authentication. Take the user login as formatting argument.

You can disable it by setting this parameter to ``None``

The default is ``"Login succeeded. Welcome, %s."`` or some translation of it
if you have enabled django internationalization (``USE_I18N = True``)


``CAS_LOGGED_MSG`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Welcome message send via the messages framework upon
authentication attempt if the user is already authenticated.
Take the user login as formatting argument.

You can disable it by setting this parameter to ``None``

The default is ``"You are logged in as %s."`` or some translation of it
if you have enabled django internationalization (``USE_I18N = True``)


``CAS_LOGIN_URL_NAME`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Name of the login url.

This is only necessary if you use the middleware and want to use some other
name for the login url (e.g. ``'my_app:cas_login'``).

The default is ``'cas_ng_login'``.


``CAS_LOGOUT_URL_NAME`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Name of the logout url.

This is only necessary if you use the middleware and
want to use some other name for the logout url (e.g. ``'my_app:cas_logout'``).

The default is ``'cas_ng_logout'``.


``CAS_EXTRA_LOGIN_PARAMS`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extra URL parameters to add to the login URL
when redirecting the user. Example::

    CAS_EXTRA_LOGIN_PARAMS = {'renew': true}

If you need these parameters to be dynamic, then we recommend to implement
a wrapper for our default login view (the same can be done in case of the
logout view). See an example in the section below.

The default is ``None``.


``CAS_RENEW`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~

Whether pass ``renew`` parameter on login and verification
of ticket to enforce that the login is made with a fresh username and password
verification in the CAS server.

The default is ``False``.


``CAS_IGNORE_REFERER`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``True``, logging out of the application will
always send the user to the URL specified by ``CAS_REDIRECT_URL``.

The default is ``False``.


``CAS_LOGOUT_COMPLETELY`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``False``, logging out of the application
won't log the user out of CAS as well.

The default is ``True``.


``CAS_REDIRECT_URL`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Where to send a user after logging in or out if
there is no referrer and no next page set. This setting also accepts named
URL patterns.

The default is ``/``.


``CAS_RETRY_LOGIN`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``True`` and an unknown or invalid ticket is
received, the user is redirected back to the login page.

The default is ``False``.


``CAS_STORE_NEXT`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``True``, the page to redirect to following login will be stored
as a session variable, which can avoid encoding errors depending on the CAS implementation.

The default is ``False``.


``CAS_VERSION`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~

The CAS protocol version to use. The following version are supported:

- ``'1'``
- ``'2'``
- ``'3'``
- ``'CAS_2_SAML_1_0'``

The default is ``'2'``.


``CAS_USERNAME_ATTRIBUTE`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The CAS user name attribute from response.
The default behaviour is to map the cas:user value to the django
username.  This attribute allows one to override this behaviour and
map a different attribute to the username e.g. mail, cn or uid.
This feature is not available when ``CAS_VERSION`` is
``'CAS_2_SAML_1_0'``.  Note that the attribute is checked before
``CAS_RENAME_ATTRIBUTES`` is applied.

The default is ``cas:user``.


``CAS_PROXY_CALLBACK`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full URL to the callback view if you want to
retrieve a Proxy Granting Ticket.

The defaults is ``None``.


``CAS_ROOT_PROXIED_AS`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Useful if behind a proxy server.  If host is listening on http://foo.bar:8080 but request
is https://foo.bar:8443.  Add CAS_ROOT_PROXIED_AS = 'https://foo.bar:8443' to your settings.


``CAS_FORCE_CHANGE_USERNAME_CASE`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``lower``, usernames returned from CAS are lowercased before
we check whether their account already exists. Allows user `Joe` to log in to CAS either as
`joe` or `JOE` without duplicate accounts being created by Django (since Django allows
case-sensitive duplicates). If ``upper``, the submitted username will be uppercased.

The default is ``False``.


``CAS_APPLY_ATTRIBUTES_TO_USER`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``True`` any attributes returned by the CAS provider
included in the ticket will be applied to the User model returned by authentication. This is
useful if your provider is including details about the User which should be reflected in your model.

The default is ``False``.


``CAS_RENAME_ATTRIBUTES`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dict used to rename the (key of the) attributes that the CAS server may retrun.
For example, if ``CAS_RENAME_ATTRIBUTES = {'ln':'last_name'}`` the ``ln`` attribute returned by the cas server
will be renamed as ``last_name``. Used with ``CAS_APPLY_ATTRIBUTES_TO_USER = True``, this provides an easy way
to fill in Django Users' info independently from the attributes' keys returned by the CAS server.


``CAS_VERIFY_SSL_CERTIFICATE`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``False`` CAS server certificate won't be verified. This is useful when using a
CAS test server with a self-signed certificate in a development environment.

.. warning::

    If ``CAS_VERIFY_SSL_CERTIFICATE`` is disabled (``False``), meaning that SSL
    certificates are not being verified by a certificate authority.
    This can expose your system to various attacks and should **never** be disabled
    in a production environment.

The default is ``True``.


``CAS_LOCAL_NAME_FIELD`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If set, will make user lookup against this field and not model's natural key.
This allows you to authenticate arbitrary users.


``CAS_FORCE_SSL_SERVICE_URL`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Available in ``4.1.0``.

Force the service url to always target HTTPS by setting ``CAS_FORCE_SSL_SERVICE_URL`` to True.

The default is ``False``.


``CAS_CHECK_NEXT`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Available in ``4.1.2``.

The URL provided by `?next` is validated so that only local URLs are allowed. This check can be disabled by
turning this setting to `False` (e.g. for local development).

The default is ``True``.


``CAS_SESSION_FACTORY`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Available in ``4.2.2``.

Can be a callable that returns a ``requests.Session`` instance. This can be used to to change behaviors when
doing HTTP requests via the underlying ``requests`` library, such as HTTP headers, proxies, hooks and more.
See `requests library documentation`_ for more details.

The default is ``None``.

Example usage:

..  code-block:: python

    from requests import Session

    def cas_get_session():
        session = Session()
        session.proxies["https"] = "http://proxy.example.org:3128"
        return session

    CAS_SESSION_FACTORY = cas_get_session


``CAS_MAP_AFFILIATIONS`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``True``, django-cas-ng will create a Django group for each
``affiliation`` that the CAS server associates with the user, during
the authentication process.

The default is ``False``.


``CAS_AFFILIATIONS_HANDLERS`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is an optional list of functions to apply to the user's CAS
affiliations. The callback is: ``handler(user, affils)``.

The default is ``[]``.


``CAS_AFFILIATIONS_KEY`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This variable defines the key used to retrieve the CAS affiliations
from the authentication attributes. If your CAS server returns the
affiliations under a different key, you can change this value accordingly.

The default is ``affiliation``.


``CAS_LOGIN_NEXT_PAGE`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The relative path where to send a user after logging in.
It may be different than CAS_REDIRECT_URL, for example if you want to use a
specific callback function.

The default is ``None``.

``CAS_LOGOUT_NEXT_PAGE`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The relative path where to send a user after logging out.
It may be different than CAS_REDIRECT_URL, for example if you want to use a
specific callback function.

The default is ``None``.


URL dispatcher
^^^^^^^^^^^^^^

Make sure your project knows how to log users in and out by adding these to
your URL mappings:

..  code-block:: python

    from django.urls import path
    import django_cas_ng.views

    urlpatterns = [
        # ...
	path('accounts/login', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
        path('accounts/logout', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
    ]

If you use the middleware, the ``login`` and ``logout`` url must be given the
name ``cas_ng_login`` and ``cas_ng_logout`` or it will create redirection
issues, unless you set the ``CAS_LOGIN_URL_NAME`` and ``CAS_LOGOUT_URL_NAME`` setting.

You should also add an URL mapping for the ``CAS_PROXY_CALLBACK`` setting, if you have this
configured:

..  code-block:: python

    path('accounts/callback', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),


Database
^^^^^^^^

Run ``./manage.py syncdb`` (or ``./manage.py migrate`` for Django 1.7+) to create Single Sign On and Proxy Granting Ticket tables.
On update you can just delete the ``django_cas_ng_sessionticket`` table and the
``django_cas_ng_proxygrantingticket`` before calling ``./manage.py syncdb``.

Consider running the command ``./manage.py django_cas_ng_clean_sessions`` on a regular basis
right after the command ``./manage.py clearsessions`` cf `clearsessions`_.
It could be a good idea to put it in the crontab.

Users should now be able to log into your site using CAS.


.. _simplified URL routing syntax: https://docs.djangoproject.com/en/dev/releases/2.0/#simplified-url-routing-syntax
.. _clearsessions: https://docs.djangoproject.com/en/1.8/topics/http/sessions/#clearing-the-session-store
.. _requests library documentation: https://docs.python-requests.org/en/master/user/advanced/#session-objects
