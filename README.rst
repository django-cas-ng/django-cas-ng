Django CAS NG
=============

.. image:: https://travis-ci.org/mingchen/django-cas-ng.svg?branch=master
    :target: https://travis-ci.org/mingchen/django-cas-ng


``django-cas-ng`` is a Central Authentication Service (CAS) client implementation.
This project inherits from `django-cas`_ (which has not been updated since
April 2013). The NG stands for "next generation". Our fork will include
bugfixes and new features contributed by the community.


Features
--------

- Supports CAS_ versions 1.0, 2.0 and 3.0.
- `Support Single Sign Out`_
- Can fetch Proxy Granting Ticket
- Supports Django 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11 and 2.0
- Supports using a `User custom model`_
- Supports Python 2.7, 3.x


Installation
------------

Install with `pip`_::

    pip install django-cas-ng


Install the latest code::

    pip install https://github.com/mingchen/django-cas-ng/archive/master.zip


Install from source code::

    python setup.py install


Settings
--------

Now add it to the middleware, authentication backends and installed apps in your settings.
Make sure you also have the authentication middleware installed.
Here's an example::

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
        ...
    )

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )

Set the following required setting in ``settings.py``:

* ``CAS_SERVER_URL``: This is the only setting you must explicitly define.
   Set it to the base URL of your CAS source (e.g. https://account.example.com/cas/).

Optional settings include:

* ``CAS_ADMIN_PREFIX``: The URL prefix of the Django administration site.
  If undefined, the CAS middleware will check the view being rendered to
  see if it lives in ``django.contrib.admin.views``.
* ``CAS_CREATE_USER``: Create a user when the CAS authentication is successful.
  The default is ``True``.
* ``CAS_CREATE_USER_WITH_ID``: Create a user using the ``id`` field provided by
  the attributes returned by the CAS provider. Default is ``False``. Raises
  ``ImproperlyConfigured`` exception if attributes are not provided or do not
  contain the field ``id``.
* ``CAS_LOGIN_MSG``: Welcome message send via the messages framework upon
  successful authentication. Take the user login as formatting argument.
  The default is ``"Login succeeded. Welcome, %s."`` or some translation of it
  if you have enabled django internationalization (``USE_I18N = True``)
  You cas disable it by setting this parametter to ``None``
* ``CAS_LOGGED_MSG``: Welcome message send via the messages framework upon
  authentication attempt if the user is already authenticated.
  Take the user login as formatting argument.
  The default is ``"You are logged in as %s."`` or some translation of it
  if you have enabled django internationalization (``USE_I18N = True``)
  You cas disable it by setting this parametter to ``None``
* ``CAS_EXTRA_LOGIN_PARAMS``: Extra URL parameters to add to the login URL
  when redirecting the user. Example::

    CAS_EXTRA_LOGIN_PARAMS = {'renew': true}

  If you need these parameters to be dynamic, then we recommend to implement
  a wrapper for our default login view (the same can be done in case of the
  logout view). See an example in the section below.

* ``CAS_RENEW``: whether pass ``renew`` parameter on login and verification
  of ticket to enforce that the login is made with a fresh username and password
  verification in the CAS server. Default is ``False``.
* ``CAS_IGNORE_REFERER``: If ``True``, logging out of the application will
  always send the user to the URL specified by ``CAS_REDIRECT_URL``.
* ``CAS_LOGOUT_COMPLETELY``: If ``False``, logging out of the application
  won't log the user out of CAS as well.
* ``CAS_REDIRECT_URL``: Where to send a user after logging in or out if
  there is no referrer and no next page set. This setting also accepts named
  URL patterns. Default is ``/``.
* ``CAS_RETRY_LOGIN``: If ``True`` and an unknown or invalid ticket is
  received, the user is redirected back to the login page.
* ``CAS_STORE_NEXT``: If ``True``, the page to redirect to following login will be stored
  as a session variable, which can avoid encoding errors depending on the CAS implementation.
* ``CAS_VERSION``: The CAS protocol version to use. ``'1'`` ``'2'`` ``'3'`` and ``'CAS_2_SAML_1_0'`` are
  supported, with ``'2'`` being the default.
* ``CAS_USERNAME_ATTRIBUTE``: The CAS user name attribute from response. The default is ``uid``.
* ``CAS_PROXY_CALLBACK``: The full url to the callback view if you want to
  retrive a Proxy Granting Ticket
* ``CAS_ROOT_PROXIED_AS``: Useful if behind a proxy server.  If host is listening on http://foo.bar:8080 but request
  is https://foo.bar:8443.  Add CAS_ROOT_PROXIED_AS = 'https://foo.bar:8443' to your settings.
* ``CAS_FORCE_CHANGE_USERNAME_CASE``: If ``lower``, usernames returned from CAS are lowercased before
  we check whether their account already exists. Allows user `Joe` to log in to CAS either as
  `joe` or `JOE` without duplicate accounts being created by Django (since Django allows
  case-sensitive duplicates). If ``upper``, the submitted username will be uppercased. Default is ``False``.
* ``CAS_APPLY_ATTRIBUTES_TO_USER``: If ``True`` any attributes returned by the CAS provider
  included in the ticket will be applied to the User model returned by authentication. This is
  useful if your provider is including details about the User which should be reflected in your model.
  The default is ``False``.
* ``CAS_RENAME_ATTRIBUTES``: a dict used to rename the (key of the) attributes that the CAS server may retrun.
  For example, if ``CAS_RENAME_ATTRIBUTES = {'ln':'last_name'}`` the ``ln`` attribute returned by the cas server
  will be renamed as ``last_name``. Used with ``CAS_APPLY_ATTRIBUTES_TO_USER = True``, this provides an easy way 
  to fill in Django Users' info independtly from the attributes' keys returned by the CAS server. 

Make sure your project knows how to log users in and out by adding these to
your URL mappings::

    import django_cas_ng.views

    url(r'^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),

You should also add an URL mapping for the ``CAS_PROXY_CALLBACK`` settings::

    url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),


Run ``./manage.py syncdb`` to create Single Sign On and Proxy Granting Ticket tables.
On update you can just delete the ``django_cas_ng_sessionticket`` table and the
``django_cas_ng_proxygrantingticket`` before calling ``./manage.py syncdb``.

Consider running the command ``./manage.py django_cas_ng_clean_sessions`` on a regular basis
right after the command ``./manage.py clearsessions`` cf `clearsessions`_.
It could be a good idea to put it in the crontab.

Users should now be able to log into your site using CAS.

View-wrappers example
---------------------

The ``settings.CAS_EXTRA_LOGIN_PARAMS`` allows you to define a static
dictionary of extra parameters to be passed on to the CAS login page. But what
if you want this dictionary to be dynamic (e.g. based on user session)?

Our current advice is to implement simple wrappers for our default views, like
these ones:

..  code-block:: python

    from django_cas_ng import views as baseviews

    @csrf_exempt
    def login(request, **kwargs):
        return _add_locale(request, baseviews.login(request, **kwargs))


    def logout(request, **kwargs):
        return _add_locale(request, baseviews.logout(request, **kwargs))


    def _add_locale(request, response):
        """If the given HttpResponse is a redirect to CAS, then add the proper
        `locale` parameter to it (and return the modified response). If not, simply
        return the original response."""

        if (
            isinstance(response, HttpResponseRedirect)
            and response['Location'].startswith(settings.CAS_SERVER_URL)
        ):
            from ourapp.some_module import get_currently_used_language
            url = response['Location']
            url += '&' if '?' in url else '&'
            url += "locale=%s" % get_currently_used_language(request)
            response['Location'] = url
        return response

Custom backends
---------------

The ``CASBackend`` class is heavily inspired from Django's own
``RemoteUserBackend`` and allows for some configurability through subclassing
if you need more control than django-cas-ng's settings provide. For instance,
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

**CASBackend.clean_username(username)**

Performs any cleaning on the ``username`` prior to using it to get or create a
``User`` object. Returns the cleaned username. The default implementations
changes the case according to the value of ``CAS_FORCE_CHANGE_USERNAME_CASE``.

**CASBackend.user_can_authenticate(user)**

Returns whether the user is allowed to authenticate. For consistency with
Django's own behavior, django-cas-ng will allow all users to authenticate
through CAS on Django versions lower than 1.10; starting with Django 1.10
however, django-cas-ng will prevent users with ``is_active=False`` from
authenticating.

**CASBackend.configure_user(user)**

Configures a newly created user. This method is called immediately after a new
user is created, and can be used to perform custom setup actions. Returns the
user object.

**CASBackend.bad_attributes_reject(request, username, attributes)**

Rejects a user if SAML username/attributes are not OK. For example, to accept a user belonging
to departmentNumber 421 only, define in ``mysite/settings.py`` the key-value constant::

    MY_SAML_CONTROL=('departmentNumber', '421')

and the authentication backends::

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
	'mysite.backends.MyCASBackend',
    ]

and create a file ``mysite/backends.py`` containing::

    from django_cas_ng.backends import CASBackend
    from django.contrib import messages
    from django.conf import settings


    class MyCASBackend(CASBackend):
        def user_can_authenticate(self, user):
            return True
    
    def bad_attributes_reject(self, request, username, attributes):
        attribute = settings.MY_SAML_CONTROL[0]
        value = settings.MY_SAML_CONTROL[1]
        
        if attribute not in attributes:
	    message = 'No \''+ attribute + '\' in SAML attributes'
	    messages.add_message(request, messages.ERROR, message)
	    return message

        if value not in attributes[attribute]:
	    message = 'User ' + str(username) + ' is not in ' + value + ' ' + attribute + ', should be one of ' + str(attributes[attribute])
            messages.add_message(request, messages.ERROR, message)
            return message

        return None


Signals
-------

django_cas_ng.signals.cas_user_authenticated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sent on successful authentication, the ``CASBackend`` will fire the ``cas_user_authenticated`` signal.

**Arguments sent with this signal**

**sender**
  The authentication backend instance that authenticated the user.

**user**
  The user instance that was just authenticated.

**created**
  Boolean as to whether the user was just created.

**attributes**
  Attributes returned during by the CAS during authentication.

**ticket**
  The ticket used to authenticate the user with the CAS.

**service**
  The service used to authenticate the user with the CAS.
  
**request**
  The request that was used to login.


django_cas_ng.signals.cas_user_logout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sent on user logout. Will be fired over manual logout or logout via CAS SingleLogOut query.

**Arguments sent with this signal**

**sender**
  ``manual`` if manual logout, ``slo`` on SingleLogOut

**user**
  The user instance that is logged out.

**session**
  The current session we are loging out.

**ticket**
  The ticket used to authenticate the user with the CAS. (if found, else value if set to ``None``)


Proxy Granting Ticket
---------------------

If you want your application to be able to issue Proxy Ticket to authenticate against some other CAS application,
setup the CAS_PROXY_CALLBACK parameter.
Allow on the CAS config django_cas_ng to act as a Proxy application.
Then after a user has logged in using the CAS, you can retrieve a Proxy Ticket as follow:

    from django_cas_ng.models import ProxyGrantingTicket

    def my_pretty_view(request, ...):
        proxy_ticket = ProxyGrantingTicket.retrieve_pt(request, service)

where ``service`` is the service url for which you want a proxy ticket.


Internationalization
--------------------

You can contribute to the translation of welcome messages by running ``django-admin makemessages -l lang_code``
inside of the django_cas_ng directory. Where ``lang_code`` is the language code for which you want to submit a
translation. Then open the file ``django_cas_ng/locale/lang_code/LC_MESSAGES/django.po`` with a gettex translations
editor (for example https://poedit.net/). Translate and save the file.
Think to add ``django_cas_ng/locale/lang_code/LC_MESSAGES/django.po`` to repo. Please do not add ``django_cas_ng/locale/lang_code/LC_MESSAGES/django.mo`` to repo since .mo file can be generated by .po file.


Testing
-------

Every code commit triggers a **travis-ci** build. checkout current build status at https://travis-ci.org/mingchen/django-cas-ng

Testing is managed by ``pytest`` and ``tox``.
Before run install, you need install required packages for testing::

    pip install -r requirements-dev.txt


To run testing on locally::

    py.test


To run all testing on all enviroments locally::

    tox


Contribution
------------

Contributions are welcome!

If you would like to contribute this project.
Please feel free to fork and send pull request.
Please make sure tests are passed.
Also welcome to add your name to **Credits** section of this document.

New code should follow both `PEP8`_ and the `Django coding style`_.


Credits
-------

* `django-cas`_
* `Stefan Horomnea`_
* `Piotr Buliński`_
* `Piper Merriam`_
* `Nathan Brown`_
* `Jason Brownbridge`_
* `Bryce Groff`_
* `Jeffrey P Gill`_
* `timkung1`_
* `Domingo Yeray Rodríguez Martín`_
* `Rayco Abad-Martín`_
* `Édouard Lopez`_
* `Guillaume Vincent`_
* `Wojciech Rygielski`_
* `Valentin Samir`_
* `Alexander Kavanaugh`_
* `Daniel Davis`_
* `Peter Baehr`_

References
----------

* `django-cas`_
* `CAS protocol`_
* `Jasig CAS server`_

.. _CAS: https://www.apereo.org/cas
.. _CAS protocol: https://www.apereo.org/cas/protocol
.. _Support Single Sign Out: https://wiki.jasig.org/display/casum/single+sign+out
.. _django-cas: https://bitbucket.org/cpcc/django-cas
.. _clearsessions: https://docs.djangoproject.com/en/1.8/topics/http/sessions/#clearing-the-session-store
.. _pip: http://www.pip-installer.org/
.. _PEP8: http://www.python.org/dev/peps/pep-0008
.. _Django coding style: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style
.. _User custom model: https://docs.djangoproject.com/en/1.5/topics/auth/customizing/
.. _Jasig CAS server: http://jasig.github.io/cas
.. _Piotr Buliński: https://github.com/piotrbulinski
.. _Stefan Horomnea: https://github.com/choosy
.. _Piper Merriam: https://github.com/pipermerriam
.. _Nathan Brown: https://github.com/tsitra
.. _Jason Brownbridge: https://github.com/jbrownbridge
.. _Bryce Groff: https://github.com/bgroff
.. _Jeffrey P Gill: https://github.com/jpg18
.. _timkung1: https://github.com/timkung1
.. _Domingo Yeray Rodríguez Martín: https://github.com/dyeray
.. _Rayco Abad-Martín: https://github.com/Rayco
.. _Édouard Lopez: https://github.com/edouard-lopez
.. _Guillaume Vincent: https://github.com/guillaumevincent
.. _Wojciech Rygielski: https://github.com/wrygiel
.. _Valentin Samir: https://github.com/nitmir
.. _Alexander Kavanaugh: https://github.com/kavdev
.. _Daniel Davis: https://github.com/danizen
.. _Peter Baehr: https://github.com/pbaehr

