.PHONY: build up tests flake8 ci tests-with-cov

include envfile
export $(shell sed 's/=.*//' envfile)

all: auth import_policy upload build run

auth:
	gcloud auth application-default login

pytest:
	python setup.py develop
	python setup.py test
	flake8 cfretl tests

build:
	docker build -t cfr-numbermuncher:latest .

gcloud_tagupload:
	docker tag cfr-numbermuncher:latest gcr.io/cfr-personalization-experiment/cfr-numbermuncher:latest
	docker push gcr.io/cfr-personalization-experiment/cfr-numbermuncher:latest


import_policy:
	gcloud dataproc autoscaling-policies import cfr-personalization-autoscale --region=$(GCLOUD_REGION) --source=./dataproc/autoscale_policy.yaml --verbosity info

upload:
	gsutil cp scripts/compute_weights.py gs://cfr-ml-jobs/compute_weights.py

run:
	# Create the bot user (not required in prod)
	docker run -it cfr-numbermuncher:latest bin/install_bot.sh

	# Spin up the docker instance to write out model weights
	docker run -v ~/.config:/app/.config \
		-e GOOGLE_CLOUD_PROJECT=moz-fx-data-derived-datasets \
		-it cfr-numbermuncher:latest python -m cfretl.main


cluster:
	gcloud dataproc clusters create cfr-sklearn-cluster3 \
		--zone=$(GCLOUD_ZONE) \
		--image-version=preview \
		--initialization-actions gs://cfr-ml-jobs/actions/python/dataproc_custom.sh

