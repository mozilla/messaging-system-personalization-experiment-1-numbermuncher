# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from cfretl import settings

import json

import requests
from requests.auth import HTTPBasicAuth


FEATURES_LIST = [
    "about_preferences_non_default_value_count",
    "active_ticks",
    "dark_mode_active",
    "firefox_accounts_configured",
    "has_at_least_one_login_saved_in_the_browser",
    "has_at_least_one_self_installed_adblocker",
    "has_at_least_one_self_installed_addon",
    "has_at_least_one_self_installed_password_manager",
    "has_at_least_one_self_installed_theme",
    "has_firefox_as_default_browser",
    "locale",
    "main_monitor_screen_width",
    "profile_age",
    "total_bookmarks_count",
    "total_uri_count",
]


class SecurityError(Exception):
    pass


class RemoteSettingsError(Exception):
    pass


def http_status_ok(status_code):
    return status_code >= 200 and status_code < 300


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
        self._kinto_bucket_path = "{base_uri:s}/buckets/{bucket:s}".format(
            base_uri=settings.KINTO_URI, bucket=settings.KINTO_BUCKET
        )
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

    def auth_get(self, url):
        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        return requests.get(url, auth=auth)

    def auth_put(self, url, jdata):
        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        return requests.put(url, json=jdata, auth=auth)

    def auth_post(self, url, jdata):
        auth = HTTPBasicAuth(self._kinto_user, self._kinto_pass)
        return requests.post(url, json=jdata, auth=auth)

    def create_user_in_test(self):
        kinto_tmpl = "{host:s}/accounts/{user:s}"
        url = kinto_tmpl.format(host=settings.KINTO_URI, user=self._kinto_user)

        status_code = self.auth_get(url).status_code
        ok = http_status_ok(status_code)
        if not ok:
            resp = self.auth_put(url, {"data": {"password": self._kinto_pass}})
            ok = http_status_ok(resp.status_code)
            print("Created user : {:s} {:b}".format(self._kinto_user, ok))
        else:
            print("User {:s} already exists".format(self._kinto_user))

    def _check_collection_exists(self, id):
        kinto_tmpl = "{bucket_path:s}/collections/{id:s}"
        url = kinto_tmpl.format(bucket_path=self._kinto_bucket_path, id=id)
        resp = self.auth_get(url)
        if not http_status_ok(resp.status_code):
            raise RemoteSettingsError(
                "HTTP Status: {}  Response Text: {} URL: {}".format(
                    resp.status_code, resp.text, url
                )
            )
        return http_status_ok(resp.status_code)

    def check_experiment_exists(self):
        return self._check_collection_exists(settings.CFR_EXPERIMENTS)

    def check_control_exists(self):
        return self._check_collection_exists(settings.CFR_CONTROL)

    def check_model_exists(self):
        return self._check_collection_exists(settings.CFR_MODEL)

    def _create_collection(self, id):
        url = "{bucket_path:s}/collections".format(bucket_path=self._kinto_bucket_path)
        status_code = self.auth_post(url, {"data": {"id": id}}).status_code
        return http_status_ok(status_code)

    def create_experiment_collection(self):
        return self._create_collection(settings.CFR_EXPERIMENTS)

    def create_control_collection(self):
        return self._create_collection(settings.CFR_CONTROL)

    def create_model_collection(self):
        return self._create_collection(settings.CFR_MODEL)

    def _test_read_cfr_control(self):
        try:
            url = "{bucket_path:s}/collections/{c_id:s}/records".format(
                bucket_path=self._kinto_bucket_path, c_id=settings.CFR_CONTROL
            )
            resp = self.auth_get(url)
            jdata = resp.json()["data"]
        except Exception:
            # This method is only used for testing purposes - it's
            # safe to just re-raise the exception here
            raise
        return jdata

    def _test_read_cfr_experimental(self):
        try:
            url = "{bucket_path:s}/collections/{c_id:s}/records".format(
                bucket_path=self._kinto_bucket_path, c_id=settings.CFR_EXPERIMENTS
            )
            resp = self.auth_get(url)
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
            # Note that this particular URL is only used during
            # debugging and we really need it to point to production
            # to get the latest `cfr` collection
            url = settings.KINTO_PROD_CFR
            resp = self.auth_get(url)
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
            url = "{bucket_path:s}/collections/{c_id:s}/records/{c_id:s}".format(
                bucket_path=self._kinto_bucket_path, c_id=settings.CFR_MODEL
            )
            resp = self.auth_get(url)
            jdata = resp.json()["data"]
            del jdata["id"]
            del jdata["last_modified"]
        except Exception:
            # This method is only used for testing purposes - it's
            # safe to just re-raise the exception here
            raise
        return jdata

    def write_models(self, json_data):
        if not self.check_model_exists():
            if not self.create_model_collection():
                raise SecurityError(
                    "{:s} collection could not be created.".format(settings.CFR_MODEL)
                )

        url = "{bucket_path:s}/collections/{c_id:s}/records/{c_id:s}".format(
            bucket_path=self._kinto_bucket_path, c_id=settings.CFR_MODEL
        )
        jdata = {"data": json_data}
        resp = self.auth_put(url, jdata)
        if http_status_ok(resp.status_code):
            print("Succesfully wrote RemoteSettings data to {:s}".format(url))
            return True

        # Raise an error so that sentry gets the error message
        err_msg = "HTTP {:d} - {:s}".format(int(resp.status_code), str(resp.text))
        raise RemoteSettingsError(err_msg)

    def cfr_records(self):
        url = "{bucket_path:s}/collections/{c_id:s}/records".format(
            bucket_path=self._kinto_bucket_path, base_uri=settings.KINTO_URI, c_id="cfr"
        )
        resp = self.auth_get(url)
        jdata = resp.json()["data"]
        cfr_records = jdata["data"]
        return cfr_records

    def _clone_cfr_to(self, cfr_data, c_id):
        for obj in cfr_data:
            # Extract the record ID so we can address it directly into
            # the cfr-control bucket
            obj_id = obj["id"]

            url = "{bucket_path:s}/collections/{c_id:s}/records/{obj_id:s}".format(
                bucket_path=self._kinto_bucket_path, c_id=c_id, obj_id=obj_id
            )
            resp = self.auth_put(url, {"data": obj})
            if resp.status_code > 299:
                print(
                    RemoteSettingsError(
                        "Error cloning CFR record id: {}".format(obj_id)
                    )
                )
            else:
                print("Cloned: {:s}/{:s}".format(c_id, obj_id))
        return True

    def clone_to_cfr_control(self, cfr_data):
        """
        Read the model from RemoteSettings.  This method is only used
        for testing
        """
        if not self.check_control_exists():
            if not self.create_control_collection():
                raise SecurityError(
                    "{} collection could not be created.".format(settings.CFR_CONTROL)
                )

        return self._clone_cfr_to(cfr_data, settings.CFR_CONTROL)

    def clone_to_cfr_experiment(self, cfr_data):
        """
        Read the model from RemoteSettings.  This method is only used
        for testing
        """
        if not self.check_experiment_exists():
            if not self.create_experiment_collection():
                raise SecurityError(
                    "{} collection could not be created.".format(
                        settings.CFR_EXPERIMENTS
                    )
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
        return self._clone_cfr_to(cfr_data, settings.CFR_EXPERIMENTS)
