
Test
====

Testing is managed by ``pytest``.

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

Tests Module Reference
----------------------

.. toctree::
   :maxdepth: 4

   modules/tests
