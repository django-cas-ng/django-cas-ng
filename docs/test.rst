
Test
====

.. image:: https://travis-ci.org/django-cas-ng/django-cas-ng.svg?branch=master
    :target: https://travis-ci.org/django-cas-ng/django-cas-ng

Every code commit triggers a **travis-ci** build. checkout current build status at https://travis-ci.org/django-cas-ng/django-cas-ng

Testing is managed by ``pytest`` and ``tox``.

Before run install, you need install required packages for testing::

    $ pip install -r requirements-dev.txt

Run Test
--------

To run testing on locally::

    $ py.test

To run testing on locally with code coverage::

    $ py.test --cov-report=html --cov=django_cas_ng
    ...
    ...
    Coverage HTML written to dir htmlcov

To run all testing on all environments locally::

    $ tox

tox.ini - tox Configuration Reference
-------------------------------------

.. literalinclude:: ../tox.ini
   :language: ini

.travis.yml - travis-ci Configuration Reference
-----------------------------------------------

.. literalinclude:: ../.travis.yml
   :language: ini

Tests Module Reference
----------------------

.. toctree::
   :maxdepth: 4

   modules/tests
