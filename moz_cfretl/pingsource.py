# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
This module loads data directly from the telemetry pings table.
"""

from google.cloud import bigquery


class BQPingLoader:
    def __init__(self):
        self._client = bigquery.Client()

    def get_pings(self, checkpoint):
        query = (
            "SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` "
            'WHERE state = "TX" '
            "LIMIT 100"
        )
        query_job = self._client.query(
            query,
            # Location must match that of the dataset(s) referenced in the query.
            location="US",
        )  # API request - starts the query

        for row in query_job:  # API request - fetches results
            # Row values can be accessed by field name or index
            assert row[0] == row.name == row["name"]

        print(row)

    def validate_remote_setting(self):
        """
        TODO: this needs to be reviewed by security review, rhelmer
        TODO: use the schema to validate the blob against:

        https://searchfox.org/mozilla-central/source/browser/components/newtab/content-src/asrouter/schemas/provider-response.schema.json
        """
        pass

    def push_remote_setting(self):
        pass
