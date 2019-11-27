# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
These tests exercise the connector to Remote Settings
"""
import pytest
import random
from cfretl.remote_settings import CFRRemoteSettings

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


@pytest.fixture
def WEIGHT_VECTOR():
    return dict(zip(CFR_IDS, [random.randint(0, 16000) for i in range(len(CFR_IDS))]))


def test_update_vector(WEIGHT_VECTOR):
    cfr_remote = CFRRemoteSettings()
    results = cfr_remote.update_weight_vector(WEIGHT_VECTOR)
    assert results == 200


@pytest.mark.skip
def test_clone_collection():
    pass


@pytest.mark.skip
def test_update_collection():
    pass


@pytest.mark.skip
def test_invalid_cfr_fails():
    pass
