"""
This script will create a cluster if required, and start the dataproc
job to write out to a table.
"""

import datetime
import json
import pkg_resources

import click
from cfretl.remote_settings import CFRRemoteSettings
from cfretl.dataproc import DataprocFacade

from cfretl import settings


def load_mock_model():
    fname = pkg_resources.resource_filename("cfretl", "scripts/cfr_ml_model.json")
    cfr_model = json.load(open(fname))["data"][0]

    # Mutate the data so we get a 'fresh' model for each update
    cfr_model["version"] = int(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    del cfr_model["id"]
    del cfr_model["last_modified"]

    return cfr_model


@click.command()
def main(cluster_name=None, zone=None, bucket_name=None, spark_filename=None):
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


if __name__ == "__main__":
    main()
