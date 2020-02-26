django-cas-ng
=============

.. image:: https://travis-ci.org/django-cas-ng/django-cas-ng.svg?branch=master
    :target: https://travis-ci.org/django-cas-ng/django-cas-ng
.. image:: https://img.shields.io/pypi/v/django-cas-ng.svg
    :target: https://pypi.org/project/django-cas-ng/
.. image:: https://img.shields.io/pypi/pyversions/django-cas-ng.svg
    :target: https://pypi.org/project/django-cas-ng/
.. image:: https://codecov.io/gh/django-cas-ng/django-cas-ng/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/django-cas-ng/django-cas-ng
.. image:: https://static.deepsource.io/deepsource-badge-light-mini.svg
    :target: https://deepsource.io/gh/django-cas-ng/django-cas-ng/?ref=repository-badge
.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
    :target: https://travis-ci.org/django-cas-ng/django-cas-ng/pull/new
.. image:: https://img.shields.io/badge/maintainers-wanted-red.svg
    :target: https://travis-ci.org/django-cas-ng/django-cas-ng

`django-cas-ng`_ is Django CAS (Central Authentication Service) 1.0/2.0/3.0 client
library to support SSO (Single Sign On) and Single Logout (SLO).

It supports Django 2.0, 2.1, 2.2, 3.0 and Python 3.5+!

This project inherits from `django-cas`_ (which has not been updated since
April 2013) at 2014. The `ng` stands for "next generation".
Our fork will include bugfixes and new features contributed by the community.

Document
--------

Checkout document at https://djangocas.dev/docs/latest/

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
- Supports Django 2.0, 2.1, 2.2 and 3.0
- Supports using a `User custom model`_
- Supports Python 3.5+
- Supports typing hints in public API.

To support django 1.x and Python 2.x, please use `3.6.0`.

Contributing
------------

New contributors are always welcome! Check out `Contribution`_ to get involved.


Change Log
----------

This project adheres to Semantic Versioning. Checkout all the `Changelog`_.


.. _django-cas-ng: https://djangocas.dev
.. _django-cas: https://bitbucket.org/cpcc/django-cas
.. _User custom model: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
.. _CAS 101: https://djangocas.dev/blog/cas-101-introduction-to-cas-central-authentication-service/
.. _Example integration: https://djangocas.dev/blog/django-cas-ng-example-project/
.. _Contribution: https://djangocas.dev/docs/latest/contribution.html
.. _Changelog: https://djangocas.dev/docs/latest/changelog.html
.. _Installation: https://djangocas.dev/docs/latest/install.html
.. _Configuration: https://djangocas.dev/docs/latest/configuration.html
