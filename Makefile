.PHONY: build up tests flake8 ci tests-with-cov

all: build

pytest:
	python setup.py develop
	python setup.py test
	flake8 cfretl tests

build:
	docker build -t cfr-numbermuncher:latest .

run:
	# Create the bot user (not required in prod)
	docker run -it cfr-numbermuncher:latest bin/install_bot.sh

	# Spin up the docker instance to write out model weights
	docker run -it cfr-numbermuncher:latest python -m cfretl.main
