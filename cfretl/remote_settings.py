# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import requests
from decouple import config


KINTO_USER = config("KINTO_USER", None)
KINTO_PASS = config("KINTO_PASS", None)


class CFRRemoteSettings:
    """
    This class can manage the Remote Settings server for CFR
    experimentation.
    """

    def __init__(self, kinto_uri, kinto_bucket, kinto_user, kinto_pass, prefix_filter="cfr-exp"):
        self._kinto_uri = kinto_uri
        self._kinto_bucket = kinto_bucket
        self._kinto_user = kinto_user
        self._kinto_pass = kinto_pass

    def get_cfr_collections(self):
        """
        Return a list of collection names with the 'cfr' prefix
        """
        requests.get()
        pass

    def clone_cfr_collection(self, src_name, dst_name):
        """
        Copy a collection from src_name to dst_name within the bucket
        """
        pass

    def update_cfr_collection(self, collection):
        pass


def write_json():
    pass
