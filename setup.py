#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    author='MING CHEN',
    author_email='mockey.chen@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
    description='CAS 1.0/2.0 authentication backend for Django (inherited from django-cas)',
    keywords='django cas cas2 sso auth authentication middleware backend',
    license='BSD',
    long_description="""
``django_cas`` is a `CAS`_ 1.0 and CAS 2.0 authentication backend for
`Django`_. It allows you to use Django's built-in authentication mechanisms
and ``User`` model while adding support for CAS.

It also includes a middleware that intercepts calls to the original login and
logout pages and forwards them to the CASified versions, and adds CAS support
to the admin interface.

**Credits**

This is project is inherited from CCPC's `django-cas`_ . 
It seems `django-cas` not update since 2013-4-1. 
I moved it github and keep github to fix exist and continue new feature develop.

.. _CAS: http://www.ja-sig.org/cas/
.. _Django: http://www.djangoproject.com/
.. _django-cas: https://bitbucket.org/cpcc/django-cas
""",
    name='django-cas-ng',
    packages=['django_cas_ng'],
    url='https://github.com/mingchen/django-cas-ng',
    version='3.0.0',
)

