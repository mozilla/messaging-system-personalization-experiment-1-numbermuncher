# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
These tests exercise the connector to Remote Settings
"""
import pytest
import random
from cfretl.remote_settings import CFRRemoteSettings

# Set a fixed random seed so that tests are stable
random.seed(42)

CFR_IDS = [
    "BOOKMARK_SYNC_CFR",
    "CRYPTOMINERS_PROTECTION",
    "CRYPTOMINERS_PROTECTION_71",
    "FACEBOOK_CONTAINER_3",
    "FACEBOOK_CONTAINER_3_72",
    "FINGERPRINTERS_PROTECTION",
    "FINGERPRINTERS_PROTECTION_71",
    "GOOGLE_TRANSLATE_3",
    "GOOGLE_TRANSLATE_3_72",
    "MILESTONE_MESSAGE",
    "PDF_URL_FFX_SEND",
    "PIN_TAB",
    "PIN_TAB_72",
    "SAVE_LOGIN",
    "SAVE_LOGIN_72",
    "SEND_RECIPE_TAB_CFR",
    "SEND_TAB_CFR",
    "SOCIAL_TRACKING_PROTECTION",
    "SOCIAL_TRACKING_PROTECTION_71",
    "WNP_MOMENTS_1",
    "WNP_MOMENTS_2",
    "WNP_MOMENTS_SYNC",
    "YOUTUBE_ENHANCE_3",
    "YOUTUBE_ENHANCE_3_72",
]


def _compare_weights(expected, actual):
    sorted_e_keys = sorted(expected.keys())
    sorted_a_keys = sorted(actual.keys())
    assert sorted_e_keys == sorted_a_keys

    sorted_e_weights = [expected[k] for k in sorted_e_keys]
    sorted_a_weights = [actual[k] for k in sorted_e_keys]

    assert sorted_e_weights == sorted_a_weights


@pytest.fixture
def WEIGHT_VECTOR():
    return dict(zip(CFR_IDS, [random.randint(0, 16000) for i in range(len(CFR_IDS))]))


def test_write_weights(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()
    assert cfr_remote.write_models(WEIGHT_VECTOR)
    actual = cfr_remote._test_read_models()
    _compare_weights(WEIGHT_VECTOR, actual)


def test_update_weights(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()

    # Pick a key
    key = iter(WEIGHT_VECTOR.keys()).__next__()

    for _ in range(3):
        WEIGHT_VECTOR[key] += 1
        assert cfr_remote.write_models(WEIGHT_VECTOR)

        actual = cfr_remote._test_read_models()
        _compare_weights(WEIGHT_VECTOR, actual)


def test_clone_into_cfr_control(MOCK_CFR_DATA):
    cfr_remote = CFRRemoteSettings()
    cfr_remote.clone_to_cfr_control(MOCK_CFR_DATA)


@pytest.mark.skip
def test_invalid_cfr_fails():
    pass
