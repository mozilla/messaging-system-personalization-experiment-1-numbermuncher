# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from decouple import config


# Default CFR Vector width is 7

CFR_VECTOR_WIDTH = config("CFR_VECTOR_WIDTH", 7)

KINTO_BUCKET = "main"

KINTO_URI = config("KINTO_URI", "http://localhost:8888/v1")
KINTO_USER = config("KINTO_USER", "admin")
KINTO_PASS = config("KINTO_PASS", "s3cr3t")
