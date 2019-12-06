# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from decouple import config


KINTO_BUCKET = "main"

KINTO_URI = config("KINTO_URI", "https://kinto.dev.mozaws.net/v1")
KINTO_USER = config("KINTO_USER", "devuser")
KINTO_PASS = config("KINTO_PASS", "devpass")
