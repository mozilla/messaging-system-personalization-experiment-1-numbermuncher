# CFR Personalization ETL Server

## Setting up your dev enviroment:

To run any of the test cases that query GCP directly, you'll need to
login to GCP using your own credentials.

From the command line - issue: `gcloud auth application-default login`


To build and startup the container - the simplest thing to do is to
run

```
make all
```

---

## Building the container

A docker file is provided to build the container.  You can issue 
`make build` to create a local image.


# Kinto authentication

The container is setup to use a default user with a username/password
pair of : (devuser, devpass) against the kinto dev server.


## Building the container

A standard Dockerfile is provided to build the container - the
simplest thing to build the container is to issue: `make build`


## Install the devuser and setup cfr-control, cfr-experiments and cfr-models

Use `make run` to spin up a testing container.

This will install initial data into the dev instance of Remote
Settings at https://kinto.dev.mozaws.net/v1 and start writing out
weight updates.  Updates are currently set as a constant of 1 second
updates to ease testing.

The `run` target will automatically mount your GCloud authentication
credentials into the `/app` home directory in the container.
