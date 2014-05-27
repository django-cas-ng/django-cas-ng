#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    author='Ming Chen',
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
    description='CAS 1.0/2.0 client authentication backend for Django (inherited from django-cas)',
    keywords=['django', 'cas', 'cas2', 'client', 'sso', 'single sign-on', 'authentication', 'auth'],
    license='BSD',
    long_description=readme,
    name='django-cas-ng',
    packages=['django_cas_ng'],
    url='https://github.com/mingchen/django-cas-ng',
    #bugtrack_url='https://github.com/mingchen/django-cas-ng/issues',  # not support this key
    download_url ='https://github.com/mingchen/django-cas-ng/releases',
    version='3.1.0',
    install_requires=['Django'],
)

