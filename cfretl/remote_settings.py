# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from cfretl import settings

import json
from jsonschema import validate


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
        if self._schema is None:
            from pkg_resources import resource_filename as resource
            self._schema = json.load(open(resource("cfretl", "schemas/cfr_weights.json"), "r"))
        return self._schema

    def update_weight_vector(self, json_data):
        validate(json_data, self.schema)
        return 200
