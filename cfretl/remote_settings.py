# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from cfretl import settings

import json

# import jsonschema
import requests
from requests.auth import HTTPBasicAuth

CFR_MODELS = "cfr-ml-model"
CFR_EXPERIMENT = "cfr-ml-experiments"
CFR_CONTROL = "cfr-ml-control"

FEATURES_LIST = [
    "have_firefox_as_default_browser",
    "active_ticks",
    "total_uri_count",
    "about_preferences_non_default_value_count",
    "has_at_least_one_self_installed_addon",
    "has_at_least_one_self_installed_password_manager",
    "has_at_least_one_self_installed_theme",
    "dark_mode_active",
    "total_bookmarks_count",
    "has_at_least_two_logins_saved_in_the_browser",
    "firefox_accounts_configured",
    "locale",
    "profile_age",
    "main_monitor_screen_width",
]


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

    def debug_load_cfr(self):
        """
        Read the production model 'cfr' collection.

        This is only used for testing and initial setup of the
        collections.
        """
        try:
            url = "https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/cfr/records"
            resp = requests.get(url)
            jdata = resp.json()
            return jdata["data"]
        except Exception:
            # This method is only used for testing purposes - it's
            # safe to just re-raise the exception here
            raise

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
        # TODO: we need a new schema validator
        # jsonschema.validate(json_data, self.schema)
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
        return True

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

        # Test CFR Message added from test plan
        # https://docs.google.com/document/d/1_aPEj_XS83qzDphOVGWk70vkbaACd270Hn9I4fY7fuE/edit#heading=h.77k16ftk1hea
        test_cfr = {
            "id": "PERSONALIZED_CFR_MESSAGE",
            "template": "cfr_doorhanger",
            "content": {
                "layout": "icon_and_message",
                "category": "cfrFeatures",
                "notification_text": "Personalized CFR Recommendation",
                "heading_text": {"string_id": "cfr-doorhanger-firefox-send-header"},
                "info_icon": {
                    "label": {"string_id": "cfr-doorhanger-extension-sumo-link"},
                    "sumo_path": "https://example.com",
                },
                "text": {"string_id": "cfr-doorhanger-firefox-send-body"},
                "icon": "chrome://branding/content/icon64.png",
                "buttons": {
                    "primary": {
                        "label": {"string_id": "cfr-doorhanger-firefox-send-ok-button"},
                        "action": {
                            "type": "OPEN_URL",
                            "data": {
                                "args": "https://send.firefox.com/login/?utm_source=activity-stream&entrypoint=activity-stream-cfr-pdf",
                                "where": "tabshifted",
                            },
                        },
                    },
                    "secondary": [
                        {
                            "label": {
                                "string_id": "cfr-doorhanger-extension-cancel-button"
                            },
                            "action": {"type": "CANCEL"},
                        },
                        {
                            "label": {
                                "string_id": "cfr-doorhanger-extension-never-show-recommendation"
                            }
                        },
                        {
                            "label": {
                                "string_id": "cfr-doorhanger-extension-manage-settings-button"
                            },
                            "action": {
                                "type": "OPEN_PREFERENCES_PAGE",
                                "data": {"category": "general-cfrfeatures"},
                            },
                        },
                    ],
                },
            },
            "targeting": "scores.PERSONALIZED_CFR_MESSAGE > scoreThreshold",
            "trigger": {"id": "openURL", "patterns": ["*://*/*.pdf"]},
        }

        for record in cfr_data:
            record[
                "targeting"
            ] = "({old_targeting:s}) && personalizedCfrScores.{id:s} > personalizedCfrThreshold".format(
                old_targeting=record["targeting"], id=record["id"]
            )
        cfr_data.append(test_cfr)
        return self._clone_cfr_to(cfr_data, CFR_EXPERIMENT)
