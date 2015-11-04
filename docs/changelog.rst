*********
Changelog
*********

Listed are the high-level, notable changes for each django-cas-ng release.
Backwards incompatible changes or other upgrade issues are also described
here. For additional detail, read the complete `commit history`_.

**django-cas-ng 3.5.0** ``[2015-11-09]``
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


