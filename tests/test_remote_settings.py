# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
These tests exercise the connector to Remote Settings
"""
from cfretl.remote_settings import CFRRemoteSettings

import pytest


def _compare_weights(expected, actual):
    sorted_e_keys = sorted(expected.keys())
    sorted_a_keys = sorted(actual.keys())
    assert sorted_e_keys == sorted_a_keys

    sorted_e_weights = [expected[k] for k in sorted_e_keys]
    sorted_a_weights = [actual[k] for k in sorted_e_keys]

    assert sorted_e_weights == sorted_a_weights


@pytest.mark.slow
def test_write_weights(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()
    assert cfr_remote.write_models(WEIGHT_VECTOR)
    actual = cfr_remote._test_read_models()
    _compare_weights(WEIGHT_VECTOR, actual)


@pytest.mark.slow
def test_update_weights(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()

    # Pick a key
    key = iter(WEIGHT_VECTOR.keys()).__next__()

    for _ in range(3):
        WEIGHT_VECTOR[key] += 1
        assert cfr_remote.write_models(WEIGHT_VECTOR)

        actual = cfr_remote._test_read_models()
        _compare_weights(WEIGHT_VECTOR, actual)


@pytest.mark.slow
def test_clone_into_cfr_control(MOCK_CFR_DATA):
    cfr_remote = CFRRemoteSettings()
    cfr_remote.clone_to_cfr_control(MOCK_CFR_DATA)

    actual = cfr_remote._test_read_cfr_control()

    actual.sort(key=lambda x: x["id"])
    MOCK_CFR_DATA.sort(key=lambda x: x["id"])

    assert len(actual) == len(MOCK_CFR_DATA)
    for a, m in zip(actual, MOCK_CFR_DATA):
        assert a["content"] == m["content"]


@pytest.mark.slow
def test_clone_into_cfr_experiment(MOCK_CFR_DATA):
    cfr_remote = CFRRemoteSettings()
    cfr_remote.clone_to_cfr_experiment(MOCK_CFR_DATA)

    _actual = cfr_remote._test_read_cfr_experimental()

    actual_target = [a for a in _actual if a["id"] == "targetting"][0]
    actual = [a for a in _actual if a["id"] != "targetting"]

    actual.sort(key=lambda x: x["id"])
    MOCK_CFR_DATA.sort(key=lambda x: x["id"])

    assert len(actual) == len(MOCK_CFR_DATA)
    for a, m in zip(actual, MOCK_CFR_DATA):
        assert a["content"] == m["content"]

    assert (
        actual_target["targetting"]
        == "scores.PERSONALIZED_CFR_MESSAGE > scoreThreshold"  # noqa: W503
    )
