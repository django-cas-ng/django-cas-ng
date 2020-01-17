Django CAS NG
=============

.. image:: https://travis-ci.org/mingchen/django-cas-ng.svg?branch=master
    :target: https://travis-ci.org/mingchen/django-cas-ng
.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
    :target: https://travis-ci.org/mingchen/django-cas-ng/pull/new
.. image:: https://img.shields.io/badge/maintainers-wanted-red.svg
    :target: https://travis-ci.org/mingchen/django-cas-ng

``django-cas-ng`` is a Central Authentication Service (CAS) client implementation.
This project inherits from `django-cas`_ (which has not been updated since
April 2013). The NG stands for "next generation". Our fork will include
bugfixes and new features contributed by the community.


Features
--------

- Supports CAS_ versions 1.0, 2.0 and 3.0.
- Support Single Sign Out
- Supports Token auth schemes
- Can fetch Proxy Granting Ticket
- Supports Django 2.0, 2.1, 2.2 and **3.0**
- Supports using a `User custom model`_
- Supports Python 3.5+


.. _CAS: https://www.apereo.org/cas
.. _django-cas: https://bitbucket.org/cpcc/django-cas
.. _clearsessions: https://docs.djangoproject.com/en/1.8/topics/http/sessions/#clearing-the-session-store
.. _User custom model: https://docs.djangoproject.com/en/1.5/topics/auth/customizing/
