= Django CAS =

`django_cas` is a [http://www.ja-sig.org/products/cas/ CAS] 1.0 and CAS 2.0
authentication backend for [http://www.djangoproject.com/ Django]. It allows
you to use Django's built-in authentication mechanisms and `User` model while
adding support for CAS.

It also includes a middleware that intercepts calls to the original login
and logout pages and forwards them to the CASified versions, and adds
CAS support to the admin interface.


== Installation ==

Run `python setup.py install`, or place the `django_cas` directory in your
`PYTHONPATH` directly. (Note: If you're using Python 2.4 or older, you'll need
to install [http://pypi.python.org/pypi/elementtree/ ElementTree] to use
CAS 2.0 functionality.)

Now add it to the middleware and authentication backends in your settings.
Make sure you also have the authentication middleware installed. Here's what
mine looks like:

{{{
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)
}}}

Set the following required setting in `settings.py`:

    * `CAS_SERVER_URL`: This is the only setting you must explicitly define.
      Set it to the base URL of your CAS source (e.g.
      http://sso.some.edu/cas/).

Optional settings include:

    * `CAS_ADMIN_PREFIX`: The URL prefix of the Django administration site.
      If undefined, the CAS middleware will check the view being rendered to
      see if it lives in `django.contrib.admin.views`.
    * `CAS_EXTRA_LOGIN_PARAMS`: Extra URL parameters to add to the login URL
      when redirecting the user.
    * `CAS_IGNORE_REFERER`: If `True`, logging out of the application will
      always send the user to the URL specified by `CAS_REDIRECT_URL`.
    * `CAS_LOGOUT_COMPLETELY`: If `False`, logging out of the application
      won't log the user out of CAS as well.
    * `CAS_REDIRECT_URL`: Where to send a user after logging in or out if
      there is no referrer and no next page set. Default is `/`.
    * `CAS_RETRY_LOGIN`: If `True` and an unknown or invalid ticket is
      received, the user is redirected back to the login page.
    * `CAS_VERSION`: The CAS protocol version to use. `'1'` and `'2'` are
      supported, with `'2'` being the default.

Make sure your project knows how to log users in and out by adding these to
your URL mappings:

{{{
(r'^accounts/login/$', 'django_cas.views.login'),
(r'^accounts/logout/$', 'django_cas.views.logout'),
}}}

Users should now be able to log into your site (and staff into the
administration interface) using CAS.


== Managing Access to the Admin Interface ==

At the moment, the best way to give a user access to the admin interface is
by doing one of the following:

    * Create the initial superuser account with a username that matches the
      desired user. `django_cas` will be able to make use of the existing
      user.
    * Similarly, create database fixtures for the superusers, and load them
      when deploying the application.
    * Ask the user to sign in to the application and, as an admin, log into
      the admin interface and change their access through the Users table.


== Populating User Data ==

To add user data, subclass `CASBackend` and specify that as your
application's backend.

For example:

{{{
from django_cas.backends import CASBackend

class PopulatedCASBackend(CASBackend):
    """CAS authentication backend with user data populated from AD"""

    def authenticate(self, ticket, service):
        """Authenticates CAS ticket and retrieves user data"""

        user = super(PopulatedCASBackend, self).authenticate(
            ticket, service)

        # Connect to AD, modify user object, etc.

        return user
}}}


== Preventing Infinite Redirects ==

Django's current implementation of its `permission_required` and
`user_passes_test` decorators (in `django.contrib.auth.decorators`) has a
known issue that can cause users to experience infinite redirects. The
decorators return the user to the login page, even if they're already logged
in, which causes a loop with SSO services like CAS.

`django_cas` provides fixed versions of these decorators in
`django_cas.decorators`. Usage is unchanged, and in the event that this issue
is fixed, the decorators should still work without issue.

For more information see http://code.djangoproject.com/ticket/4617.


== Customizing the 403 Error Page ==

Django doesn't provide a simple way to customize 403 error pages, so you'll
have to make a response middleware that handles `HttpResponseForbidden`.

For example, in `views.py`:

{{{
from django.http import HttpResponseForbidden
from django.template import RequestContext, loader

def forbidden(request, template_name='403.html'):
    """Default 403 handler"""

    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))
}}}

And in `middleware.py`:

{{{
from django.http import HttpResponseForbidden

from yourapp.views import forbidden

class Custom403Middleware(object):
      """Catches 403 responses and renders 403.html"""

      def process_response(self, request, response):

          if isinstance(response, HttpResponseForbidden):
             return forbidden(request)
          else:
             return response
}}}

Now add `yourapp.middleware.Custom403Middleware` to your `MIDDLEWARE_CLASSES`
setting and create a template named `403.html`.

== CAS 2.0 support ==

The CAS 2.0 protocol is supported in the same way that 1.0 is; no extensions
or new features from the CAS 2.0 specification are implemented. `elementtree`
is required to use this functionality. (`elementtree` is also included in
Python 2.5's standard library.)

Note: The CAS 3.x server uses the CAS 2.0 protocol. There is no CAS 3.0
protocol, though the CAS 3.x server does allow extensions to the protocol.


== Differences Between Django CAS 1.0 and 2.0 ==

Version 2.0 of `django_cas` breaks compatibility in some small ways, in order
simplify the library. The following settings have been removed:

    * `CAS_LOGIN_URL` and `CAS_LOGOUT_URL`: Version 2.0 is capable of
      determining these automatically.
    * `CAS_POPULATE_USER`: Subclass `CASBackend` instead (see above).
    * `CAS_REDIRECT_FIELD_NAME`: Django's own `REDIRECT_FIELD_NAME` is now
      used unconditionally.
