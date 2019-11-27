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
import contextlib
from cfretl import CFR_VECTOR_WIDTH
from jsonschema import validate

LIMIT_CLAUSE = ""
BQ_DATE_FORMAT = "%Y-%m-%d %H:00:00"


class InvalidVector(Exception):
    pass


class BQPingLoader:
    def __init__(self):
        # The BigQuery client is lazily bound so that tests run fast
        self._bqclient = None

    @property
    def _client(self):
        if self._bqclient is None:
            self._bqclient = bigquery.Client()
        return self._bqclient

    def build_query(self, dt, limit_rowcount=None):
        start_dt = datetime.datetime(
            dt.year, dt.month, dt.day, dt.hour, 0, 0, tzinfo=pytz.utc
        )
        end_dt = start_dt + timedelta(hours=1)

        start_ts = start_dt.strftime(BQ_DATE_FORMAT)
        end_ts = end_dt.strftime(BQ_DATE_FORMAT)

        query_tmpl = (
            "select * from `moz-fx-data-bq-srg`.tiles.assa_events_daily "
            "where receive_at >= '{start_ts:s}' and "
            "receive_at <= '{end_ts:s}' {limit_clause:s}"
        )

        if limit_rowcount is None:
            limit = LIMIT_CLAUSE
        else:
            limit = "limit {:d} ".format(limit_rowcount)

        query = query_tmpl.format(start_ts=start_ts, end_ts=end_ts, limit_clause=limit)
        return query.strip()

    def get_pings(self, dt=None, limit_rowcount=None, as_dict=False):
        query = self.build_query(dt, limit_rowcount=limit_rowcount)
        query_job = self._client.query(
            query,
            # Location must match that of the dataset(s) referenced in the query.
            location="US",
        )  # API request - starts the query

        print("Running : {:s}".format(query))
        for i in query_job:
            if as_dict:
                yield dict([(k, i[k]) for k in i.keys()])
            else:
                yield i

    def compute_vector_weights(self):
        for row in self.get_pings():
            # Run the pings through the model here
            pass

        with self.compute_new_vector() as new_vector:
            self.validate_vector(new_vector)
            self.write_vector(new_vector)

    @contextlib.contextmanager
    def compute_new_vector(self):
        # TODO: implement the model update here
        yield [1, 2, 3, 4, 5]

    def validate_vector(self, vector):
        """
        TODO: this needs to be reviewed by security review, rhelmer
        TODO: use the schema to validate the blob against:

        https://searchfox.org/mozilla-central/source/browser/components/newtab/content-src/asrouter/schemas/provider-response.schema.json
        """

        schema = {
            "$schema": "https://json-schema.org/schema#",
            "type": "object",
            "properties": {
                "weights": {
                    "type": "array",
                    "minItems": CFR_VECTOR_WIDTH,
                    "maxItems": CFR_VECTOR_WIDTH,
                    "items": {"type": "integer"},
                }
            },
            "required": ["weights"],
        }
        validate(vector, schema)

    def write_vector(self, vector):
        """
        TODO: this needs to be reviewed by security review, rhelmer
        TODO: use the schema to validate the blob against:

        https://searchfox.org/mozilla-central/source/browser/components/newtab/content-src/asrouter/schemas/provider-response.schema.json
        """
        pass

    def push_remote_setting(self):
        pass
