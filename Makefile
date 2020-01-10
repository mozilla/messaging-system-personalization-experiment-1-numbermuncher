.PHONY: build up tests flake8 ci tests-with-cov

include envfile
export $(shell sed 's/=.*//' envfile)

all: auth import_policy upload build run

auth:
	gcloud auth application-default login

pytest:
	pip install -r requirements.txt
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

run:
	# Spin up the docker instance to write out model weights
	docker run -v ~/.config:/app/.config \
		-e GCLOUD_PROJECT=cfr-personalization-project \
		-it cfr-numbermuncher:latest

run_gcr:
	# Spin up the docker instance to write out model weights
	docker run -v ~/.config:/app/.config \
		-e GOOGLE_CLOUD_PROJECT=cfr-personalization-experiment \
		-e TEST_PREFIX=vng1 \
		-it gcr.io/cfr-personalization-experiment/cfr-numbermuncher:latest

bash_gcr:
	# Start up bash in the container
	docker run -v ~/.config:/app/.config \
				-e GOOGLE_CLOUD_PROJECT=cfr-personalization-experiment \
				-e TEST_PREFIX=vng1 \
				--entrypoint=/bin/bash  \
				-it gcr.io/cfr-personalization-experiment/cfr-numbermuncher:latest


cluster:
	gcloud dataproc clusters create cfr-sklearn-cluster3 \
		--zone=$(GCLOUD_ZONE) \
		--image-version=preview \
		--initialization-actions gs://cfr-ml-jobs/actions/python/dataproc_custom.sh

