# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from unittest.mock import MagicMock
from cfretl.pingsource import BQPingLoader
import datetime
import pytz


@pytest.fixture
def FIXTURE_JSON():
    return {
        "client_id": "5caa92ae-e078-4f18-bbaf-bd23094a4a1a",
        "addon_version": "2018.08.22.1219-93becf29",
        "source": "TOP_SITES",
        "session_id": "{8435349f-bf5d-41e5-b4df-cc94821db032}",
        "page": "about:newtab",
        "action_position": "13",
        "event": "CLICK",
        "receive_at": datetime.datetime(2018, 9, 30, 10, 51, 40, tzinfo=pytz.utc),
        "date": datetime.date(2018, 9, 30),
        "locale": "en-US",
        "country_code": "LV",
        "os": "Windows 7",
        "browser": "Firefox",
        "version": "62.0.2",
        "device": "Other",
        "user_prefs": 43,
        "release_channel": "release",
        "shield_id": "n/a",
        "sample_id": 63,
        "value": '{"card_type": "pinned", "icon_type": "screenshot_with_icon"}',
    }


@pytest.fixture
def bqpl(FIXTURE_JSON):
    bqpl = BQPingLoader()

    # Clobber the inbound pings
    bqpl.get_pings = MagicMock(return_value=[FIXTURE_JSON])

    # Clobber the model generation
    bqpl.compute_vector_weights = MagicMock(return_value={'weights': [2, 5, 9, 23, 5, 8, 12]})

    return bqpl
