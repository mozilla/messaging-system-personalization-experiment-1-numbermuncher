.PHONY: build up tests flake8 ci tests-with-cov

all: auth build run

auth:
	gcloud auth application-default login

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
	docker run -v ~/.config:/app/.config \
		-e GOOGLE_CLOUD_PROJECT=moz-fx-data-derived-datasets \
		-it cfr-numbermuncher:latest python -m cfretl.main
