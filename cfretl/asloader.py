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

        query_tmpl = (
            "select * from `moz-fx-data-bq-srg`.tiles.assa_router_events_daily "
            "where receive_at >= '{start_ts:s}' and "
            "receive_at <= '{end_ts:s}' {limit_clause:s}"
        )

        if limit_rowcount is None:
            limit = LIMIT_CLAUSE
        else:
            limit = "limit {:d} ".format(limit_rowcount)

        query = query_tmpl.format(start_ts=start_ts, end_ts=end_ts, limit_clause=limit)
        return query.strip()

    def _get_pings(self, dt=None, limit_rowcount=None, as_dict=False):
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
        for row in self._get_pings():
            # Run the pings through the model here
            pass

        # TODO: do soemthing here to build a model
        raise NotImplementedError()
