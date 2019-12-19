# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
These tests exercise the connector to Remote Settings
"""
from cfretl.remote_settings import CFRRemoteSettings

import pytest
import json


def _compare_weights(json1, json2):
    assert json.dumps(sorted(json1), indent=2) == json.dumps(sorted(json2), indent=2)


@pytest.fixture
def MOCK_CFR_DATA():
    cfr_remote = CFRRemoteSettings()
    return cfr_remote.debug_load_cfr()


@pytest.mark.slow
def test_write_weights(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()
    assert cfr_remote.write_models(WEIGHT_VECTOR)
    actual = cfr_remote._test_read_models()
    _compare_weights(WEIGHT_VECTOR, actual)


@pytest.mark.slow
def test_update_weights(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()
    assert cfr_remote.write_models(WEIGHT_VECTOR)

    actual = cfr_remote._test_read_models()
    assert actual == WEIGHT_VECTOR


@pytest.mark.slow
def test_clone_into_cfr_control(MOCK_CFR_DATA):
    cfr_remote = CFRRemoteSettings()
    cfr_remote.clone_to_cfr_control(MOCK_CFR_DATA)

    actual = cfr_remote._test_read_cfr_control()

    actual_ids = set([obj["id"] for obj in actual])
    expected_ids = set([obj["id"] for obj in MOCK_CFR_DATA])

    diff = actual_ids.difference(expected_ids)
    assert ("panel_local_testing" in diff and len(diff) == 1) or (len(diff) == 0)


@pytest.mark.slow
def test_clone_into_cfr_experiment(MOCK_CFR_DATA):
    cfr_remote = CFRRemoteSettings()
    cfr_remote.clone_to_cfr_experiment(MOCK_CFR_DATA)

    actual = cfr_remote._test_read_cfr_experimental()

    actual_ids = set([obj["id"] for obj in actual])
    expected_ids = set([obj["id"] for obj in MOCK_CFR_DATA])

    diff = actual_ids.difference(expected_ids)

    # Check that we have targetting added
    assert "targetting" in actual_ids
    diff.remove("targetting")

    assert ("panel_local_testing" in diff and len(diff) == 1) or (len(diff) == 0)
