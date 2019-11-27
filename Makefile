.PHONY: build up tests flake8 ci tests-with-cov

pytest:
	python setup.py develop
	python setup.py test
	flake8 moz_cfretl tests

build:
	docker build -t cfr-personalization:latest .

up:
	docker -e KINTO_USER=${KINTO_USER} -e KINTO_PASS=${KINTO_PASS} run cfr-personalization:latest
