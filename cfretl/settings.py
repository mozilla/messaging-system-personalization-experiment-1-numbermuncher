# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from decouple import config

TEST_PREFIX = config("TEST_PREFIX", "")

KINTO_BUCKET = "main"

KINTO_URI = config("KINTO_URI", "https://kinto.dev.mozaws.net/v1")
KINTO_USER = config("KINTO_USER", TEST_PREFIX + "devuser")
KINTO_PASS = config("KINTO_PASS", TEST_PREFIX + "devpass")

GCP_PROJECT_ID = config("GCP_PROJECT_ID", "cfr-personalization-experiment")
DATAPROC_CLUSTER = config("DATAPROC_CLUSTER", "cfr-experiments")
GCP_ZONE = config("GCP_ZONE", "us-west1-a")

GCS_BUCKET_NAME = config("GCS_BUCKET_NAME", "cfr-ml-jobs")
DATAPROC_SCRIPT = config("DATAPROC_SCRIPT", "compute_weights.py")

CFR_MODEL = config("CFR_MODEL", TEST_PREFIX + "cfr-ml-model")
CFR_EXPERIMENTS = config("CFR_EXPERIMENTS", TEST_PREFIX + "cfr-ml-experiments")
CFR_CONTROL = config("CFR_CONTROL", TEST_PREFIX + "cfr-ml-control")
