# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from cfretl import settings

import json
import jsonschema
import requests
from requests.auth import HTTPBasicAuth

CFR_MODELS = "cfr-models"
CFR_EXPERIMENT = "cfr-experiment"
CFR_CONTROL = "cfr-control"


class CFRRemoteSettings:
    """
    This class can manage the Remote Settings server for CFR
    experimentation.

    We only write to a single collection: 'cfr-experiment'

    The other collections related to this experiment must be loaded
    manually and go through the regular dual sign off process.

    For reference, those collections are called:

    'cfr-control' and 'cfr-models'.

    See "CFR Machine Learning Experiment" doc for full details.
    """

    def __init__(self):
        self._kinto_uri = settings.KINTO_URI
        self._kinto_bucket = settings.KINTO_BUCKET
        self._kinto_user = settings.KINTO_USER
        self._kinto_pass = settings.KINTO_PASS

        self._schema = None

    @property
    def schema(self):
        # Lazily load the CFR Weights schema
        if self._schema is None:
            from pkg_resources import resource_filename as resource

            self._schema = json.load(
                open(resource("cfretl", "schemas/cfr_weights.json"), "r")
            )
        return self._schema

    def _check_collection_exists(self, id):
        kinto_tmpl = "{host:s}/buckets/{bucket:s}/collections/{id:s}"
        url = kinto_tmpl.format(host=self._kinto_uri, bucket=self._kinto_bucket, id=id)
        resp = requests.get(url)
        return resp.status_code >= 200 and resp.status_code < 300

    def check_weights_exists(self):
        return self._check_collection_exists(self._weight_collection)

    def check_control_exists(self):
        return self._check_collection_exists(self._control_collection)

    def check_model_exists(self):
        return self._check_collection_exists(self._model_collection)

    def _create_collection(self, id):
        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        url = "{base_uri:s}/buckets/main/collections".format(base_uri=self._kinto_uri)
        status_code = requests.post(
            url, json={"data": {"id": CFR_EXPERIMENT}}, auth=auth
        ).status_code
        return status_code >= 200 and status_code < 300

    def create_weights_collection(self):
        return self._create_collection(CFR_EXPERIMENT)

    def create_control_collection(self):
        return self._create_collection(CFR_CONTROL)

    def create_model_collection(self):
        return self._create_collection(CFR_MODELS)

    def write_weights(self, json_data):
        jsonschema.validate(json_data, self.schema)

        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        url = "{base_uri:s}/buckets/main/collections/{id:s}".format(
            base_uri=self._kinto_uri, id=CFR_EXPERIMENT
        )

        resp = requests.post(url, json=json_data, auth=auth)
        return resp.status_code >= 200 and resp.status_code < 300
