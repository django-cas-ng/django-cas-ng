*********************
How To Make A Release
*********************

1. Update `docs/changelog.txt`
2. Update version in `docs/conf.py`, `setup.py`.
3. commit changes.
4. Tag a version, e.g.

    git tag v3.2.0

5. Upload release to pypi.python.org

    python setup.py sdist upload    

6. Create a new release on github.com and upload `django-cas-ng-x.x.x.tar.gz`
    https://github.com/mingchen/django-cas-ng/releases
