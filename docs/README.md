# CFR Machine Learning

[![Build Status](https://travis-ci.org/mozilla/cfr-personalization.svg?branch=master)](https://travis-ci.org/mozilla/cfr-personalization)

# Table of Contents (ToC):

- [How does it work?](#how-does-it-work)
- [Building and Running tests](#build-and-run-tests)

## How does it work?

CFR Personalization is done inside of a Dataproc cluster in GCP.

In Dataproc - a PySpark job is run over BigQuery tables from the
telemetry feeds.  

In the context of Remote Settings, CFR uses the 'main' bucket.

Each 'Provider ID' in the about:newtab#devtools page is called a
'collection' in Remote Settings.

To minimize impact on production, we constrain the places where
we can write into the 'main' bucket.

![Collections are not 'Buckets'](./rs_collections.jpg "Collections are not Buckets")

## Building and running tests

You should be able to build cfr-personalization using Python 3.7

To run the testsuite, execute ::

```python
$ python setup.py develop
$ python setup.py test
```
