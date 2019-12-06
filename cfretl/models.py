# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json


class CFRModel:
    def _one_cfr_model_feature(self, cfr_id, feature_id, p0, p1):
        """
        Generate the JSON data structure for a single CFR feature (accept, reject) pair
        """
        snippet = """{{"{cfr_id:s}": {{
                      "{feature_id:s}": {{
                            "p_given_cfr_acceptance": {p0:0.09f},
                            "p_given_cfr_rejection": {p1:0.09f}
                            }}}}}}"""

        txt = snippet.format(cfr_id=cfr_id, feature_id=feature_id, p0=p0, p1=p1)
        jdata = json.loads(txt)
        return jdata

    def generate_cfr_model(self, cfr_model_cfg, version):
        """
        Generate the complete cfr-ml-models data
        """
        model_cfrid = {}
        for cfr_id, cfr_cfg in cfr_model_cfg.items():
            if cfr_id not in model_cfrid:
                model_cfrid[cfr_id] = {}

            prior_p0 = cfr_cfg["p0"]
            prior_p1 = cfr_cfg["p1"]

            for feature in cfr_cfg["features"]:
                feature_dict = self._one_cfr_model_feature(
                    cfr_id, feature["feature_id"], feature["p0"], feature["p1"]
                )

                model_cfrid[cfr_id].update(feature_dict[cfr_id])
                model_cfrid[cfr_id].update(
                    json.loads(
                        """{{"prior_cfr": {{"p_acceptance": {:0.09f}, "p_rejection": {:0.09f}}}}}""".format(
                            prior_p0, prior_p1
                        )
                    )
                )
        model = {"models_by_cfr_id": model_cfrid, "version": version}
        return model
