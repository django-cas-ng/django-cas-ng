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


``CAS_ADMIN_PREFIX`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The URL prefix of the Django administration site.
If undefined, the CAS middleware will check the view being rendered to
see if it lives in ``django.contrib.admin.views``.

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

You cas disable it by setting this parametter to ``None``

The default is ``"Login succeeded. Welcome, %s."`` or some translation of it
if you have enabled django internationalization (``USE_I18N = True``)


``CAS_LOGGED_MSG`` [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Welcome message send via the messages framework upon
authentication attempt if the user is already authenticated.
Take the user login as formatting argument.

You cas disable it by setting this parametter to ``None``

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
If set with a value other than ``uid`` when ``CAS_VERSION`` is not ``'CAS_2_SAML_1_0'``, this
will be handled by the ``CASBackend``, in which case if the user lacks that attribute then
authentication will fail. Note that the attribute is checked before ``CAS_RENAME_ATTRIBUTES``
is applied.

The default is ``uid``.


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

URL dispatcher
^^^^^^^^^^^^^^

Make sure your project knows how to log users in and out by adding these to
your URL mappings, noting the `simplified URL routing syntax`_ in Django 2.0
and later:

..  code-block:: python

    # Django 2.0+
    from django.urls import path
    import django_cas_ng.views

    urlpatterns = [
        # ...
	path('accounts/login', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
        path('accounts/logout', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
    ]

..  code-block:: python

    # Django < 2.0
    from django.conf.urls import url
    import django_cas_ng.views

    urlpatterns = [
        # ...
        url(r'^accounts/login$', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
        url(r'^accounts/logout$', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
    ]


If you use the middleware, the ``login`` and ``logout`` url must be given the
name ``cas_ng_login`` and ``cas_ng_logout`` or it will create redirection
issues, unless you set the ``CAS_LOGIN_URL_NAME`` and ``CAS_LOGOUT_URL_NAME`` setting.

You should also add an URL mapping for the ``CAS_PROXY_CALLBACK`` setting, if you have this
configured:

..  code-block:: python

    # Django 2.0+
    path('accounts/callback', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),

..  code-block:: python

    # Django < 2.0
    url(r'^accounts/callback$', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),


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
