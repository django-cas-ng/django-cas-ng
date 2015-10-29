PYTHON=python

all: build

build: compilemessages
	$(PYTHON) setup.py build

clean:
	$(PYTHON) setup.py clean --all
	rm -rf build dist django_cas_ng.egg-info temp
	find . -name '*.py[co]' -exec rm -f "{}" ';'
	find . -name '*.mo' -exec rm -f "{}" ';'

install: compilemessages
	$(PYTHON) setup.py install

compilemessages:
	cd django_cas_ng && django-admin compilemessages
