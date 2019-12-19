"""
This script will create a cluster if required, and start the dataproc
job to write out to a table.
"""

import argparse
import datetime
import json
import pkg_resources
import time

from flask import Flask
from dockerflow.flask import Dockerflow
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from cfretl.remote_settings import CFRRemoteSettings
from cfretl.dataproc import DataprocFacade

from cfretl import settings

app = Flask(__name__)
dockerflow = Dockerflow(app)

sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[FlaskIntegration()])


def load_mock_model():
    fname = pkg_resources.resource_filename("cfretl", "scripts/cfr_ml_model.json")
    cfr_model = json.load(open(fname))["data"][0]

    # Mutate the data so we get a 'fresh' model for each update
    cfr_model["version"] = int(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    del cfr_model["id"]
    del cfr_model["last_modified"]

    return cfr_model


@app.route("/")
def main():
    # The DataprocFacade will manage cluster creation
    # and destruction once the context exits
    with DataprocFacade(
        settings.GCP_PROJECT_ID, settings.DATAPROC_CLUSTER, settings.GCP_ZONE
    ) as dataproc:
        # Upload the script from the cfretl.scripts directory

        # TODO: this should just pass in a filename - a cluster
        # is only going to run a single job anyway
        dataproc.upload_sparkjob(settings.GCS_BUCKET_NAME, settings.DATAPROC_SCRIPT)

        # TODO: should probably pass a token in here so that we
        # can verify that results were successfully computed
        dataproc.run_job(settings.GCS_BUCKET_NAME, settings.DATAPROC_SCRIPT)

        remote_settings = CFRRemoteSettings()
        remote_settings.create_user_in_test()

        # TODO: do something to test that we have results we're looking for
        # and transform the bq result table
        # into a final model
        model = load_mock_model()
        remote_settings.write_models(model)


def start_flask():
    parser = argparse.ArgumentParser(description="Start the flask service")
    parser.add_argument("--port", type=int, default=8000, help="Port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Hostname")
    args = parser.parse_args()

    app.run(host=args.host, port=int(args.port))


if __name__ == "__main__":
    while True:
        main()
        time.sleep(60 * 10)
