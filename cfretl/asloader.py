# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
This module loads data directly from the telemetry pings table.
"""

from google.cloud import bigquery
from datetime import timedelta
import datetime
import pytz
import logging

LIMIT_CLAUSE = ""
BQ_DATE_FORMAT = "%Y-%m-%d %H:00:00"


class InvalidVector(Exception):
    pass


class ASLoader:
    def __init__(self):
        # The BigQuery client is lazily bound so that tests run fast
        self._bqclient = None

    @property
    def _client(self):
        if self._bqclient is None:
            self._bqclient = bigquery.Client()
        return self._bqclient

    def _build_query(self, dt, limit_rowcount=None):
        start_dt = datetime.datetime(
            dt.year, dt.month, dt.day, dt.hour, 0, 0, tzinfo=pytz.utc
        )
        end_dt = start_dt + timedelta(hours=1)

        start_ts = start_dt.strftime(BQ_DATE_FORMAT)
        end_ts = end_dt.strftime(BQ_DATE_FORMAT)

        # production query will be different
        query_tmpl = (
            "select * from `moz-fx-data-shar-nonprod-efed`.messaging_system_live.cfr_v1 "
            "where submission_timestamp > '{start_ts:s}' and submission_timestamp <= '{end_ts:s}' "
            "limit 10"
        )

        query = query_tmpl.format(start_ts=start_ts, end_ts=end_ts)
        return query.strip()

    def _get_pings(self, dt=None, limit_rowcount=None, as_dict=False):
        if dt is None:
            logging.warn("No date was specified - defaulting to 7 days ago for an hour")
            dt = datetime.datetime.now() - timedelta(days=7)

        query = self._build_query(dt, limit_rowcount=limit_rowcount)
        query_job = self._client.query(
            query,
            # Location must match that of the dataset(s) referenced in the query.
            location="US",
        )  # API request - starts the query

        logging.info("Running : {:s}".format(query))
        for i in query_job:
            if as_dict:
                yield dict([(k, i[k]) for k in i.keys()])
            else:
                yield i

    def compute_vector_weights(self):
        assert len([row for row in self._get_pings()]) > 0
        # TODO: Call out to dataproc to compute the model here
        # raise NotImplementedError()
