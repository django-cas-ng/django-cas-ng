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

    python setup.py sdist upload    

    or 

    python setup.py sdist
    twine upload dist/django-cas-ng-3.5.9.tar.gz

8. Create a new release on https://github.com/mingchen/django-cas-ng/releases
