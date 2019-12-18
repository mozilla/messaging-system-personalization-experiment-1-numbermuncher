"""
This script will create a cluster if required, and start the dataproc
job to write out to a table.
"""

import datetime
import random
import json
import pkg_resources

import click
from cfretl.remote_settings import CFRRemoteSettings
from cfretl.dataproc import DataprocFacade


def load_mock_model():
    fname = pkg_resources.resource_filename("cfretl", "scripts/cfr_ml_model.json")
    cfr_model = json.load(open(fname))["data"][0]

    # Mutate the data so we get a 'fresh' model for each update
    cfr_model["version"] = int(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    for model in cfr_model["models_by_cfr_id"].values():
        for k, v in model.items():
            if k == "prior_cfr":
                continue
            v["p_given_cfr_acceptance"] = random.random()
            v["p_given_cfr_rejection"] = random.random()

    return cfr_model


@click.command()
@click.option("--project-id", default="cfr-personalization-experiment")
@click.option("--cluster-name", default="cfr-experiments")
@click.option("--zone", default="us-west1-a")
@click.option("--bucket-name", default="cfr-ml-jobs")
@click.option("--spark-filename", default="compute_weights.py")
def main(
    project_id=None, cluster_name=None, zone=None, bucket_name=None, spark_filename=None
):

    # The DataprocFacade will manage cluster creation
    # and destruction once the context exits
    with DataprocFacade(project_id, cluster_name, zone) as dataproc:
        # Upload the script from the cfretl.scripts directory

        # TODO: this should just pass in a filename - a cluster
        # is only going to run a single job anyway
        dataproc.upload_sparkjob(bucket_name, spark_filename)

        # TODO: should probably pass a token in here so that we
        # can verify that results were successfully computed
        dataproc.run_job(bucket_name, spark_filename)

        remote_settings = CFRRemoteSettings()

        # TODO: do something to test that we have results we're looking for
        # and transform the bq result table
        # into a final model
        model = load_mock_model()
        remote_settings.write_models(model)


if __name__ == "__main__":
    main()
