*********
Changelog
*********

Listed are the high-level, notable changes for each django-cas-ng release.
Backwards incompatible changes or other upgrade issues are also described
here. For additional detail, read the complete `commit history`_.

**django-cas-ng 3.5.9** ``[2018-01-02]``

  * Add the optional setting CAS_CREATE_USER_WITH_ID. (PR #129)
  * Fix get_proxy_ticket method usage. (PR #131)
  * Add django 2.0 compability. (PR #143 #146)
  * Added bad_attributes_reject to check SAML key/value attributes. (PR #145)

**django-cas-ng 3.5.8** ``[2017-06-30]``

  * Upgrade django-cas to 1.2.0
  * Fix: Coerce boolean strings in attributes to actual boolean values
  * Update middleware for consistency with new-style django middleware
  * Add CAS_APPLY_ATTRIBUTES_TO_USER  new settings option to apply attributes to User model.
  * Add support for applying attributes returned from ticket to User model


**django-cas-ng 3.5.7** ``[2016-11-06]``

  * Added the request to the signals
  * Address #114 by providing a setting `CAS_STORE_NEXT`
  * Change authenticate() argument order for changes in Django 1.11
  * CAS_REDIRECT_URL should accept named URL patterns
  * Add requests to requirements


**django-cas-ng 3.5.6** ``[2016-11-06]``

* Depends python_cas>=1.2.0


**django-cas-ng 3.5.5** ``[2016-09-28]``

* Login after the session is created, fix the need for double login (such as #83, might fix it but seems slightly
different)
* Fix #96 Login after the session is created, fix the need for double login
* Fix #95 by delete django requirement from setup.py
* Fix #91 - raise PermissionDenied rather than return HttpResponseForbidden
* Add check_additional_permissions to the backend. This allows one to subclass the backend and add arbitrary user permissions checks when authenticating.


**django-cas-ng 3.5.4** ``[2016-04-27]``

* Support for string view arguments to url() is deprecated and will be removed in Django 1.10.
* Add migrations.
* Add initial migrations file.
* Add CAS_FORCE_CHANGE_USERNAME_CASE option to convert username case to lower or upper. This prevent duplicate account
creation in some case.
* Bugfix for loop redirect when CAS_ADMIN_PREFIX is set as root.


**django-cas-ng 3.5.3** ``[2015-11-20]``

* Add translation mo files into release build.


**django-cas-ng 3.5.2** ``[2015-11-19]``

* Add python-cas to install_requires.


**django-cas-ng 3.5.1** ``[2015-11-10]``

* Remove the auto_now and keep the auto_now_add per the documentation.


**django-cas-ng 3.5.0** ``[2015-11-08]``

* Add support for Proxy Granting Ticket.
* Add Single Logout support.
* Add Python3 support.
* Add Django 1.8 support.
* Add support for custom user model.
* Add CAS_USERNAME_ATTRIBUTE which allows picking an alternative variable to store the username in the cas attributes.
* Add CAS_DISPLAY_LOGIN_MESSAGE setting to control whether show welcome message, default is true.
* Fix redirecting with the "?next" parameter.

**django-cas-ng 3.4.2** ``[2015-01-11]``

* Fix forbidden error.
* Add CAS_CREATE_USER setting to control over whether or not a user is created.

**django-cas-ng 3.4.1** ``[2014-11-27]``

* Specific django version in dependence.
* Removed the ticket GET param from the service, as it could break CAS.

**django-cas-ng 3.4.0** ``[2014-11-12]``

* Add signal support ``django_cas_ng.signals.cas_user_authenticated``
* Add python 3.4 test env

**django-cas-ng 3.3.0** ``[2014-11-05]``

* Support Django 1.7
* Integrate with travis-ci

**django-cas-ng 3.2.0** ``[2014-10-25]``

* Add CAS_RENEW setting to enforce CAS renew feature. Default is False.
* Port to Python 3 (Python 2 also supported)
* Allow multiple attributes with the same name for CAS3


**django-cas-ng 3.1.0** ``[2014-05-25]``
   * Support Django 1.5 custom user model.

.. _commit history: https://github.com/mingchen/django-cas-ng/commits


