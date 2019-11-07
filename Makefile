.PHONY: build up tests flake8 ci tests-with-cov

all:
	# PySpark only knows eggs, not wheels
	python setup.py sdist

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

pytest:
	python setup.py develop
	python setup.py test
	flake8 taar tests

build:
	docker build -t cfr-personalization:latest .
