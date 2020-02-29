Signals
=======

*Signals* allow decoupled applications get notified when actions occur elsewhere in the framework.
In a nutshell, signals allow certain senders to notify a set of receivers that some action has taken place.

*django-cas-ng* defines two signals:

* `cas_user_authenticated`
* `cas_user_logout`

django_cas_ng.signals.cas_user_authenticated
--------------------------------------------

Sent on successful authentication, the ``CASBackend`` will fire the ``cas_user_authenticated`` signal.

**Arguments sent with this signal**

**sender**
  [CASBackend] The authentication backend instance that authenticated the user.

**user**
  [str] The user instance that was just authenticated.

**created**
  [bool] Boolean as to whether the user was just created.

**attributes**
  [Dict] Attributes returned during by the CAS during authentication.

**ticket**
  [str] The ticket used to authenticate the user with the CAS.

**service**
  [str] The service used to authenticate the user with the CAS.

**request**
  [HttpRequest] The request that was used to login.


django_cas_ng.signals.cas_user_logout
-------------------------------------

Sent on user logout. Will be fired over manual logout or logout via CAS SingleLogOut query.

**Arguments sent with this signal**

**sender**
  [str] ``manual`` if manual logout, ``slo`` on SingleLogOut

**user**
  [str] The user instance that is logged out.

**session**
  [Session] The current session we are loging out.

**ticket**
  [str] The ticket used to authenticate the user with the CAS.
  (if found, else value if set to ``None``)


Receiver Example
----------------

Here is a simple example to use `@receiver` decorator to receive signals.

You can also check
`the signal usage in example app <https://github.com/django-cas-ng/example/blob/master/mysite/signals.py>`_.

..  code-block:: python

    #
    # File: signals.py
    #

    import json

    from django.dispatch import receiver
    from django_cas_ng.signals import cas_user_authenticated, cas_user_logout


    @receiver(cas_user_authenticated)
    def cas_user_authenticated_callback(sender, **kwargs):
        args = {}
        args.update(kwargs)
        print('''cas_user_authenticated_callback:
        user: %s
        created: %s
        attributes: %s
        ''' % (
            args.get('user'),
            args.get('created'),
            json.dumps(args.get('attributes'), sort_keys=True, indent=2)))


    @receiver(cas_user_logout)
    def cas_user_logout_callback(sender, **kwargs):
        args = {}
        args.update(kwargs)
        print('''cas_user_logout_callback:
        user: %s
        session: %s
        ticket: %s
        ''' % (
            args.get('user'),
            args.get('session'),
            args.get('ticket')))

Test cases
----------

Also checkout the test cases source code to see it usage.

.. automodule:: tests.test_signals
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

References
----------

* `signals.py in example app <https://github.com/django-cas-ng/example/blob/master/mysite/signals.py>`_
* `Django document: Signals <https://docs.djangoproject.com/en/3.0/topics/signals/>`_
