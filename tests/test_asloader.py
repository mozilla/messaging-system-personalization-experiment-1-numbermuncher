# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
These tests exercise the connector to Remote Settings
"""
import pytz
from cfretl.asloader import ASLoader
import datetime


def test_build_query():
    """
    Test that we can fetch a single hour worth of data
    """
    asloader = ASLoader()
    d = datetime.datetime(2019, 11, 27, 12, 11, 0, tzinfo=pytz.utc)
    sql = asloader._build_query(d)
    # The minute section should be zeroed out
    expected = "select * from `moz-fx-data-bq-srg`.tiles.assa_router_events_daily where receive_at >= '2019-11-27 12:00:00' and receive_at <= '2019-11-27 13:00:00'"
    assert expected == sql


def test_fetch_pings(asloader, FIXTURE_JSON):
    # Test that our mock ASLoader returns a single ping
    dt = datetime.datetime(2018, 9, 30, 10, 1, tzinfo=pytz.utc)
    row_iter = asloader._get_pings(dt, limit_rowcount=1, as_dict=True)
    rows = [i for i in row_iter]
    assert rows[0] == FIXTURE_JSON


def test_compute_vector(asloader, WEIGHT_VECTOR):
    """
    Check that the vector is validated against a JSON schema
    """

    # Well formed vectors should pass
    vector = asloader.compute_vector_weights()
    assert vector == WEIGHT_VECTOR

    # Full vector validation is done when we write to Remote Settings
