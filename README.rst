Django CAS NG
=============

.. image:: https://travis-ci.org/mingchen/django-cas-ng.svg?branch=master
    :target: https://travis-ci.org/mingchen/django-cas-ng
.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
    :target: https://travis-ci.org/mingchen/django-cas-ng/pull/new
.. image:: https://img.shields.io/badge/maintainers-wanted-red.svg
    :target: https://travis-ci.org/mingchen/django-cas-ng

`django-cas-ng`_ is a Central Authentication Service (CAS) client implementation.
This project inherits from `django-cas`_ (which has not been updated since
April 2013). The NG stands for "next generation". Our fork will include
bugfixes and new features contributed by the community.


Document
--------

Checkout document at https://djangocas.dev/docs/

Quick links:

* `CAS Protocol Introduction`_
* `Installation`_
* `Configuration`_

Features
--------

- Supports CAS_ versions 1.0, 2.0 and 3.0.
- Support Single Sign Out
- Supports Token auth schemes
- Can fetch Proxy Granting Ticket
- Supports Django 2.0, 2.1, 2.2 and **3.0**
- Supports using a `User custom model`_
- Supports Python 3.5+

Contributing
------------

New contributors are always welcome! Check out `Contribution`_ to get involved.


Change Log
----------
This project adheres to Semantic Versioning. Checkout all the `Changelog`_.


.. _CAS: https://www.apereo.org/cas
.. _django-cas-ng: https://djangocas.dev
.. _django-cas: https://bitbucket.org/cpcc/django-cas
.. _User custom model: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
.. _CAS Protocol Introduction: https://djangocas.dev/docs/4.0/cas-protocol.html
.. _Contribution: https://djangocas.dev/docs/4.0/contribution.html
.. _Changelog: https://djangocas.dev/docs/4.0/changelog.html
.. _Installation: https://djangocas.dev/docs/4.0/install.html
.. _Configuration: https://djangocas.dev/docs/4.0/configuration.html

