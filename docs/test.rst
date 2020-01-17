
Test
----

Every code commit triggers a **travis-ci** build. checkout current build status at https://travis-ci.org/mingchen/django-cas-ng

Testing is managed by ``pytest`` and ``tox``.
Before run install, you need install required packages for testing::

    pip install -r requirements-dev.txt


To run testing on locally::

    py.test


To run all testing on all enviroments locally::

    tox
