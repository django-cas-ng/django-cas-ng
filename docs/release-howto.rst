:orphan:

*********************
How To Make A Release
*********************

1. Update `docs/changelog.txt`
2. Update version in `docs/conf.py`, `setup.py`.
3. commit changes.
4. Tag a version, e.g.

    git tag v3.2.0

5. push changes:

    git push
    git push --tags

6. Build project. This will generate translated language files.

    make build

7. Upload release to pypi.python.org

    # update setuptools if needed.
    #pip install -U pip setuptools twine

    pip install wheel
    python setup.py sdist bdist_wheel upload

    or

    pip install twine
    python setup.py sdist bdist_wheel
    twine upload dist/django-cas-ng-4.3.0.tar.gz dist/django_cas_ng-4.3.0-py2.py3-none-any.whl

8. Create a new release on https://github.com/mingchen/django-cas-ng/releases


Troubleshooting

    $ make build
    CommandError: Can't find msgfmt. Make sure you have GNU gettext tools 0.15 or newer installed.

    $ brew install gettext
    $ export PATH=$PATH:/usr/local/Cellar/gettext/0.19.8.1/bin
    $ make build


    error: invalid command 'bdist_wheel'

    $ pip install wheel
