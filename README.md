## Setting up your dev enviroment:

To run any of the test cases that query GCP directly, you'll need to
login to GCP using your own credentials.

From the command line - issue: `gcloud auth application-default login`

Long version:
For the full details, see: https://docs.telemetry.mozilla.org/cookbooks/bigquery.html#from-client-sdks


# Testing the container

The container is setup to use a default user with the following
settings:

Username: devuser
Password: devpass


## Building the container

```
make build
```


## Install the devuser and setup cfr-control, cfr-experiments and cfr-models


This will install initial data into the dev instance of Remote
Settings at https://kinto.dev.mozaws.net/v1 and start writing out
weight updates.  Updates are currently set as a constant of 1 second
updates to ease testing.

```
make run
```
