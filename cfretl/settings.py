# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from decouple import config

# This is only required in the dev enviroment
# to prevent midair collisions testing with devuser/devpass
TEST_PREFIX = config("TEST_PREFIX", "")

SENTRY_DSN = config("SENTRY_DSN", '')

KINTO_URI = config("KINTO_URI", "https://kinto.dev.mozaws.net/v1")
KINTO_USER = config("KINTO_USER", TEST_PREFIX + "devuser")
KINTO_PASS = config("KINTO_PASS", TEST_PREFIX + "devpass")

KINTO_BUCKET = config("KINTO_BUCKET", "main")

KINTO_PROD_CFR = config("KINTO_PROD_CFR", "https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/cfr/records")

# This specifies the GCP project we are running in
GCP_PROJECT_ID = config("GCP_PROJECT_ID", "cfr-personalization-experiment")

# The dataproc cluster name can be redefined if necessary
DATAPROC_CLUSTER = config("DATAPROC_CLUSTER", "cfr-experiments")

# The Dataproc cluster must be created within a zone. The region is
# automatically computed from the zone definition.
GCP_ZONE = config("GCP_ZONE", "us-west1-a")

# This is the GCS bucket where the Dataproc job will live
GCS_BUCKET_NAME = config("GCS_BUCKET_NAME", "cfr-ml-jobs")

# The script from cfretl.scripts which will be uploaded into GCS
DATAPROC_SCRIPT = config("DATAPROC_SCRIPT", "compute_weights.py")

# Override auto subnetwork allocation for custom subnetworks
DATAPROC_SUBNETWORK_URI = config("DATAPROC_SUBNETWORK_URI", "auto")

# Override default dataproc service account
DATAPROC_SERVICE_ACCOUNT = config("DATAPROC_SERVICE_ACCOUNT", None)

# These are names of the RemoteSettings collections in the main bucket
# None of these should need to be modified.
CFR_MODEL = config("CFR_MODEL", TEST_PREFIX + "cfr-ml-models")
CFR_EXPERIMENTS = config("CFR_EXPERIMENTS", TEST_PREFIX + "cfr-ml-experiments")
CFR_CONTROL = config("CFR_CONTROL", TEST_PREFIX + "cfr-ml-control")
