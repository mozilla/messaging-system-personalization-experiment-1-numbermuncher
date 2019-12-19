"""
This script installs fixture test data into a kinto server
"""

from cfretl.remote_settings import CFRRemoteSettings
from cfretl.remote_settings import FEATURES_LIST
from cfretl.models import CFRModel
import random
from datetime import datetime
import time

random.seed(time.time())

remote_settings = CFRRemoteSettings()

version_code = int(datetime.utcnow().strftime("%Y%m%d%H%m%S"))

CFRS = remote_settings.debug_load_cfr()
CFR_ID_LIST = [r["id"] for r in CFRS]


def generate_cfr_cfgdata(version_code):
    """
    This function will need to be rewritten to parse the
    BQ output table and coerce it into values for RemoteSettings JSON
    blob
    """
    model = CFRModel()

    data = []
    for idx, cfr_id in enumerate(CFR_ID_LIST):
        prior_0 = random.random()
        snip = model.one_cfr(
            cfr_id,
            [prior_0, 1 - prior_0],
            [
                [random.randint(1, 10000) for i in FEATURES_LIST],
                [random.randint(1, 10000) for i in FEATURES_LIST],
            ],
        )
        data.append(snip)

    return model.generate_cfr_model(data, version_code)


remote_settings.create_user_in_test()

remote_settings.clone_to_cfr_control(CFRS)
remote_settings.clone_to_cfr_experiment(CFRS)

json_model = generate_cfr_cfgdata(version_code)
remote_settings.write_models(json_model)
print("Wrote out version : {:d}".format(version_code))
print("=" * 20, datetime.now(), "=" * 20)
