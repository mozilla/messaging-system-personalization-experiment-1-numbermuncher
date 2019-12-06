"""
This script installs fixture test data into a kinto server
"""

from cfretl.remote_settings import CFRRemoteSettings
from cfretl.remote_settings import FEATURES_LIST
from cfretl.models import CFRModel
import random
from datetime import datetime

remote_settings = CFRRemoteSettings()

version_code = int(datetime.utcnow().strftime("%Y%m%d%H%m%S"))

CFRS = remote_settings.debug_load_cfr()
CFR_ID_LIST = [r["id"] for r in CFRS]


def generate_cfr_cfgdata():
    """
    This function will need to be rewritten to parse the
    BQ output table and coerce it into values for RemoteSettings JSON
    blob
    """
    cfg_data = {}
    for cfr_id in CFR_ID_LIST:

        # TODO: replace this with prior 0
        p0 = random.random()

        cfg_data[cfr_id] = {"p0": p0, "p1": 1 - p0, "features": []}
        for f_id in FEATURES_LIST:
            cfg_data[cfr_id]["features"].append(
                {"feature_id": f_id, "p0": random.random(), "p1": random.random()}
            )
    return cfg_data


model = CFRModel()
json_model = model.generate_cfr_model(generate_cfr_cfgdata(), version_code)
remote_settings.write_models(json_model)

remote_settings.clone_to_cfr_control(CFRS)
remote_settings.clone_to_cfr_experiment(CFRS)
print("Wrote out version : {:d}".format(version_code))
print("=" * 20, datetime.now(), "=" * 20)
