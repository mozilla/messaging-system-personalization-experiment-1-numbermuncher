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


class SecurityError(Exception):
    pass


class RemoteSettingWriteError(Exception):
    pass


class CFRRemoteSettings:
    """
    This class can manage the Remote Settings server for CFR
    experimentation.

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

    def check_experiment_exists(self):
        return self._check_collection_exists(CFR_EXPERIMENT)

    def check_control_exists(self):
        return self._check_collection_exists(CFR_CONTROL)

    def check_model_exists(self):
        return self._check_collection_exists(CFR_MODELS)

    def _create_collection(self, id):
        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        url = "{base_uri:s}/buckets/main/collections".format(base_uri=self._kinto_uri)
        status_code = requests.post(
            url, json={"data": {"id": id}}, auth=auth
        ).status_code
        return status_code >= 200 and status_code < 300

    def create_experiment_collection(self):
        return self._create_collection(CFR_EXPERIMENT)

    def create_control_collection(self):
        return self._create_collection(CFR_CONTROL)

    def create_model_collection(self):
        return self._create_collection(CFR_MODELS)

    def _test_read_cfr_control(self):
        try:
            url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records".format(
                base_uri=self._kinto_uri, c_id=CFR_CONTROL
            )
            resp = requests.get(url)
            jdata = resp.json()["data"]
        except Exception:
            # This method is only used for testing purposes - it's
            # safe to just re-raise the exception here
            raise
        return jdata

    def _test_read_cfr_experimental(self):
        try:
            url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records".format(
                base_uri=self._kinto_uri, c_id=CFR_EXPERIMENT
            )
            resp = requests.get(url)
            jdata = resp.json()["data"]
        except Exception:
            # This method is only used for testing purposes - it's
            # safe to just re-raise the exception here
            raise
        return jdata

    def _test_read_models(self):
        """
        Read the model from RemoteSettings.  This method is only used
        for testing
        """
        try:
            url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records/{c_id:s}".format(
                base_uri=self._kinto_uri, c_id=CFR_MODELS
            )
            resp = requests.get(url)
            jdata = resp.json()["data"]
            del jdata["id"]
            del jdata["last_modified"]
        except Exception:
            # This method is only used for testing purposes - it's
            # safe to just re-raise the exception here
            raise
        return jdata

    def write_models(self, json_data):
        jsonschema.validate(json_data, self.schema)
        if not self.check_model_exists():
            if not self.create_model_collection():
                raise SecurityError("cfr-model collection could not be created.")

        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records/{c_id:s}".format(
            base_uri=self._kinto_uri, c_id=CFR_MODELS
        )

        jdata = {"data": json_data}
        resp = requests.put(url, json=jdata, auth=auth)

        return resp.status_code >= 200 and resp.status_code < 300

    def cfr_records(self):
        url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records".format(
            base_uri=self._kinto_uri, c_id="cfr"
        )
        resp = requests.get(url)
        jdata = resp.json()["data"]
        cfr_records = jdata["data"]
        return cfr_records

    def _clone_cfr_to(self, cfr_data, c_id):
        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)

        for obj in cfr_data:
            # Extract the record ID so we can address it directly into
            # the cfr-control bucket
            obj_id = obj["id"]

            url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records/{obj_id:s}".format(
                base_uri=self._kinto_uri, c_id=c_id, obj_id=obj_id
            )
            resp = requests.put(url, json={"data": obj}, auth=auth)
            if resp.status_code > 299:
                raise RemoteSettingWriteError(
                    "Error cloning CFR record id: {}".format(obj_id)
                )

    def clone_to_cfr_control(self, cfr_data):
        """
        Read the model from RemoteSettings.  This method is only used
        for testing
        """
        if not self.check_control_exists():
            if not self.create_control_collection():
                raise SecurityError(
                    "{} collection could not be created.".format(CFR_CONTROL)
                )

        return self._clone_cfr_to(cfr_data, CFR_CONTROL)

    def clone_to_cfr_experiment(self, cfr_data):
        """
        Read the model from RemoteSettings.  This method is only used
        for testing
        """
        if not self.check_experiment_exists():
            if not self.create_experiment_collection():
                raise SecurityError(
                    "{} collection could not be created.".format(CFR_EXPERIMENT)
                )

        self._clone_cfr_to(cfr_data, CFR_EXPERIMENT)
        # Write in the targetting attribute

        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        obj_id = "targetting"
        url = "{base_uri:s}/buckets/main/collections/{c_id:s}/records/{obj_id:s}".format(
            base_uri=self._kinto_uri, c_id=CFR_EXPERIMENT, obj_id=obj_id
        )
        obj = {"targetting": "scores.PERSONALIZED_CFR_MESSAGE > scoreThreshold"}
        resp = requests.put(url, json={"data": obj}, auth=auth)
        if resp.status_code > 299:
            raise RemoteSettingWriteError(
                "Error writing targetting expression to experiment bucket"
            )
