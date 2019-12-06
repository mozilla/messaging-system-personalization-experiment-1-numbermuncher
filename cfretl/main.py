"""
This script will create a cluster if required, and start the dataproc
job to write out to a table.
"""

import json
import pkg_resources

import click
from cfretl.remote_settings import CFRRemoteSettings
from cfretl.dataproc import DataprocFacade


def load_mock_model():
    fname = pkg_resources.resource_filename("cfretl", "scripts/cfr_ml_model.json")
    mock_model = json.load(open(fname))["data"][0]
    return mock_model


@click.command()
@click.option("--project-id", default="cfr-personalization-experiment")
@click.option("--cluster-name", default="cfr-experiments")
@click.option("--zone", default="us-west1-a")
@click.option("--bucket-name", default="cfr-ml-jobs")
@click.option("--spark-filename", default="compute_weights.py")
def main(
    project_id=None, cluster_name=None, zone=None, bucket_name=None, spark_filename=None
):
    dataproc = DataprocFacade(project_id, cluster_name, zone)
    dataproc.create_cluster_if_not_exists()

    # Upload the script from teh cfretl.scripts directory
    dataproc.upload_sparkjob(bucket_name, spark_filename)
    dataproc.run_job(bucket_name, spark_filename)

    # TODO: do something to transform the bq result table
    # into a final model

    remote_settings = CFRRemoteSettings()
    remote_settings.write_models(load_mock_model())

    dataproc.destroy_cluster()


if __name__ == "__main__":
    main()
