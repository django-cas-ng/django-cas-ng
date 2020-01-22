Signals
=======

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
