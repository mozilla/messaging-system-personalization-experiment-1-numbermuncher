# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import numpy as np


class CFRModel:
    def one_cfr(self, cfr_id, priors, neg_probs):
        # Force these to be np array types
        priors = np.array(priors)
        neg_probs = np.array(neg_probs)

        assert len(priors) == 2

        assert len(neg_probs) == 2
        assert len(neg_probs[0]) == len(neg_probs[1])

        del_probs = np.transpose(neg_probs)

        snippet = {
            "{:s}".format(cfr_id): {
                "priors": priors.tolist(),
                "negProbs": neg_probs.tolist(),
                "delProbs": del_probs.tolist(),
            }
        }
        return snippet

    def generate_cfr_model(self, cfr_snip_list, version):
        models_by_cfr_id = {}
        for snip in cfr_snip_list:
            models_by_cfr_id.update(snip)

        return {"version": version, "models_by_cfr_id": models_by_cfr_id}
