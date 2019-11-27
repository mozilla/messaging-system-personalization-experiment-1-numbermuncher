# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
These tests exercise the connector to Remote Settings
"""
import pytz
import pytest
from cfretl.pingsource import BQPingLoader
import datetime

import jsonschema


def test_build_query():
    """
    Test that we can fetch a single hour worth of data
    """
    bqpl = BQPingLoader()
    d = datetime.datetime(2019, 11, 27, 12, 11, 0, tzinfo=pytz.utc)
    sql = bqpl.build_query(d)
    # The minute section should be zeroed out
    expected = "select * from `moz-fx-data-bq-srg`.tiles.assa_events_daily where receive_at >= '2019-11-27 12:00:00' and receive_at <= '2019-11-27 13:00:00'"
    assert expected == sql


def test_fetch_pings(bqpl, FIXTURE_JSON):
    # Test that our mock BQPL returns a single ping
    dt = datetime.datetime(2018, 9, 30, 10, 1, tzinfo=pytz.utc)
    row_iter = bqpl.get_pings(dt, limit_rowcount=1, as_dict=True)
    rows = [i for i in row_iter]
    assert rows[0] == FIXTURE_JSON


def test_validate_vector(bqpl):
    """
    Check that the vector is validated against a JSON schema
    """

    # Well formed vectors should pass
    vector = bqpl.compute_vector_weights()
    bqpl.validate_vector(vector)

    # vector must be wrapped in a dict
    vector = [2, 5, 9, 23, 5, 8, 12]
    with pytest.raises(jsonschema.exceptions.ValidationError):
        bqpl.validate_vector(vector)

    # vector must have no strings
    vector = {"weights": [2, 5, "9", 23, 5, 8, 12]}
    with pytest.raises(jsonschema.exceptions.ValidationError):
        bqpl.validate_vector(vector)
