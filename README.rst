django-cas-ng
=============
.. image:: https://img.shields.io/pypi/v/django-cas-ng.svg
    :target: https://pypi.org/project/django-cas-ng/
.. image:: https://img.shields.io/pypi/pyversions/django-cas-ng.svg
    :target: https://pypi.org/project/django-cas-ng/
.. image:: https://codecov.io/gh/django-cas-ng/django-cas-ng/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/django-cas-ng/django-cas-ng
.. image:: https://static.deepsource.io/deepsource-badge-light-mini.svg
    :target: https://deepsource.io/gh/django-cas-ng/django-cas-ng/?ref=repository-badge

django-cas-ng is a Django CAS (Central Authentication Service) 1.0/2.0/3.0 client
library to support SSO (Single Sign-On) and Single Logout (SLO).

It supports Django 5.2+ and Python 3.10+.

Documentation
--------

Documentation can be seen here: https://github.com/django-cas-ng/django-cas-ng/tree/master/docs.
Parts of this may be out-of-date, the documentation has not been updated recently.

Quick links:

* `CAS 101`_: Introduction to CAS protocol.
* `Example integration`_: A step by step guide on how to integrate this library.
* `Installation`_
* `Configuration`_

Features
--------

- Supports **CAS** versions 1.0, 2.0 and 3.0
- Support Single Logout (needs CAS server support)
- Supports Token auth schemes
- Can fetch Proxy Granting Ticket
- Supports Django 5.2+
- Supports using a `Custom User model`_
- Supports Python 3.10+
- Supports typing hints in public API.

Contributing
------------

New contributors are always welcome! Check out `Contribution`_ to get involved.


Changelog
----------

Recent changes are here: https://github.com/django-cas-ng/django-cas-ng/releases

Pre-5.0.0 changelog: https://djangocas.dev/docs/latest/changelog.html


.. _django-cas: https://bitbucket.org/cpcc/django-cas
.. _Custom User model: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/
.. _CAS 101: https://djangocas.dev/blog/cas-101-introduction-to-cas-central-authentication-service/
.. _Example integration: https://djangocas.dev/blog/django-cas-ng-example-project/
.. _Contribution: https://djangocas.dev/docs/latest/contribution.html
.. _Installation: https://djangocas.dev/docs/latest/install.html
.. _Configuration: https://djangocas.dev/docs/latest/configuration.html
