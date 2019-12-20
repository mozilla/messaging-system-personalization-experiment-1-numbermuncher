import pkg_resources
import time

from google.cloud import bigquery
from google.cloud import dataproc_v1
from google.cloud import storage
from google.cloud.dataproc_v1.gapic.transports import cluster_controller_grpc_transport
from google.cloud.dataproc_v1.gapic.transports import job_controller_grpc_transport

from cfretl import settings


waiting_callback = False


def cluster_callback(operation_future):
    # Reset global when callback returns.
    global waiting_callback
    waiting_callback = False


def wait_for_cluster_create():
    """Wait for cluster creation."""
    print("Waiting for cluster creation...")

    while True:
        if not waiting_callback:
            print("Cluster created.")
            break


def wait_for_cluster_delete():
    """Wait for cluster creation."""
    print("Waiting for cluster deletion...")

    while True:
        if not waiting_callback:
            print("Cluster deleted.")
            break


class DataprocFacade:
    """
    This class exposes a minimal interface to execute PySpark jobs on
    Dataproc.

    Basic features include:

    * Creating a custom dataproc cluster if one does not exist
    * Execution of the script and emitting output to a BigQuery table
    """

    def __init__(self, project_id, cluster_name, zone):
        self._project_id = project_id
        self._cluster_name = cluster_name
        self._zone = zone
        self._region = self._get_region_from_zone(zone)

        self._dataproc_cluster_client = None
        self._dataproc_job_client = None

    def __enter__(self):
        self.install_node_config()
        if self.cluster_exists():
            raise RuntimeError("Dataproc cluster already exists - terminating job")
        self.create_cluster_if_not_exists()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.delete_cluster_if_exists()

    def install_node_config(self):
        src_name = pkg_resources.resource_filename(
            "cfretl", "scripts/dataproc_custom.sh"
        )
        dst_name = "actions/python/dataproc_custom.sh"
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(dst_name)
        blob.upload_from_filename(src_name)
        print("Uploaded {} to {}".format(src_name, dst_name))

    def dataproc_job_client(self):
        """
        Lazily obtain a GCP Dataproc JobController client
        """
        if self._dataproc_job_client is None:
            job_transport = job_controller_grpc_transport.JobControllerGrpcTransport(
                address="{}-dataproc.googleapis.com:443".format(self._region)
            )
            self._dataproc_job_client = dataproc_v1.JobControllerClient(job_transport)
        return self._dataproc_job_client

    def dataproc_cluster_client(self):
        """
        Lazily create a Dataproc ClusterController client to setup or
        tear down dataproc clusters
        """

        if self._dataproc_cluster_client is None:
            client_transport = cluster_controller_grpc_transport.ClusterControllerGrpcTransport(
                address="{}-dataproc.googleapis.com:443".format(self._region)
            )
            self._dataproc_cluster_client = dataproc_v1.ClusterControllerClient(
                client_transport
            )
        return self._dataproc_cluster_client

    def delete_cluster_if_exists(self):
        """
        Destroy the Dataproc cluster if it exists
        """
        try:
            if self.cluster_exists():
                self._delete_cluster()
                wait_for_cluster_delete()
            else:
                print("Cluster {} already exists.".format(self._cluster_name))
        except Exception as exc:
            raise exc

    def create_cluster_if_not_exists(self):
        """
        Create Dataproc cluster if one doesn't exist yet
        """
        try:
            if not self.cluster_exists():
                self._create_cluster()
                wait_for_cluster_create()
            else:
                print("Cluster {} already exists.".format(self._cluster_name))
        except Exception as exc:
            raise exc

    def cluster_exists(self):
        """
        Check that the Dataproc Cluster exists
        """
        try:
            return self.dataproc_cluster_client().get_cluster(
                self._project_id, self._region, self._cluster_name
            )
        except Exception:
            return False

    def check_jobexists(self, bucket_name, filename):
        """
        Check that a pyspark script exists in Google Cloud Storage
        """
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        return blob.exists()

    def upload_sparkjob(self, bucket_name, src_name):
        """
        Uploads a PySpark file to GCS bucket for later executino
        """
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(src_name)
        blob.upload_from_filename(
            pkg_resources.resource_filename("cfretl", "scripts/{}".format(src_name))
        )
        print("Uploaded {} to {}".format(src_name, src_name))

    def run_job(self, bucket_name, spark_filename):
        """
        Execute a PySpark job from a GCS bucket in our Dataproc cluster
        """
        job_id = self._submit_pyspark_job(bucket_name, spark_filename)
        self._wait_for_job(job_id)

    def copy_bq_table(self, dataset_name, src_tbl, dst_tbl):
        """
        Copy a BigQuery table in this project
        """
        client = bigquery.Client()
        dataset = client.dataset(dataset_name)
        src = dataset.table(src_tbl)
        dst = dataset.table(dst_tbl)
        src_name = ".".join([src._project, src._dataset_id, src.table_id])
        dst_name = ".".join([dst._project, dst._dataset_id, dst.table_id])
        copy_job = client.copy_table(src_name, dst_name)
        copy_job.done()

    #  Internal Methods
    #

    def _delete_cluster(self):
        cluster = self.dataproc_cluster_client().delete_cluster(
            self._project_id, self._region, self._cluster_name
        )
        cluster.add_done_callback(cluster_callback)
        global waiting_callback
        waiting_callback = True

    def _get_region_from_zone(self, zone):
        try:
            region_as_list = zone.split("-")[:-1]
            return "-".join(region_as_list)
        except (AttributeError, IndexError, ValueError):
            raise ValueError("Invalid zone provided, please check your input.")

    def _create_cluster(self):
        """Create the cluster."""

        # TODO: pass in the bucket somehow. maybe an attribute
        # settings
        # bucket_name = "cfr-ml-jobs"

        print("Creating cluster...")
        cluster_config = {
            "cluster_name": self._cluster_name,
            "project_id": self._project_id,
            "config": {
                "gce_cluster_config": {
                    "subnetwork_uri": settings.DATAPROC_SUBNETWORK_URI
                },
                "master_config": {
                    "num_instances": 1,
                    "machine_type_uri": "n1-standard-1",
                    "disk_config": {
                        "boot_disk_type": "pd-ssd",
                        "num_local_ssds": 1,
                        "boot_disk_size_gb": 1000,
                    },
                },
                "worker_config": {
                    "num_instances": 2,
                    "machine_type_uri": "n1-standard-8",
                    "disk_config": {
                        "boot_disk_type": "pd-ssd",
                        "num_local_ssds": 1,
                        "boot_disk_size_gb": 1000,
                    },
                },
                "autoscaling_config": {
                    "policy_uri": "projects/{gcp_project:s}/regions/{region:s}/autoscalingPolicies/cfr-personalization-autoscale".format(
                        gcp_project=settings.GCP_PROJECT_ID, region=self._region
                    )
                },
                "initialization_actions": [
                    {
                        "executable_file": "gs://{gcs_bucket:s}/actions/python/dataproc_custom.sh".format(
                            gcs_bucket=settings.GCS_BUCKET_NAME
                        )
                    }
                ],
                "software_config": {"image_version": "1.4.16-ubuntu18"},
            },
        }

        cluster = self.dataproc_cluster_client().create_cluster(
            self._project_id, self._region, cluster_config
        )
        cluster.add_done_callback(cluster_callback)
        global waiting_callback
        waiting_callback = True

    def _submit_pyspark_job(self, bucket_name, filename):
        """Submit the Pyspark job to the cluster (assumes `filename` was uploaded
        to `bucket_name.

        Note that the bigquery connector is added at job submission
        time and not cluster creation time.
        """
        job_details = {
            "placement": {"cluster_name": self._cluster_name},
            "pyspark_job": {
                "main_python_file_uri": "gs://{}/{}".format(bucket_name, filename),
                "jar_file_uris": ["gs://spark-lib/bigquery/spark-bigquery-latest.jar"],
            },
        }

        result = self.dataproc_job_client().submit_job(
            project_id=self._project_id, region=self._region, job=job_details
        )
        job_id = result.reference.job_id
        print("Submitted job ID {}.".format(job_id))
        return job_id

    def _wait_for_job(self, job_id):
        """Wait for job to complete or error out."""
        print("Waiting for job to finish...")
        while True:
            job = self.dataproc_job_client().get_job(
                self._project_id, self._region, job_id
            )
            # Handle exceptions
            if job.status.State.Name(job.status.state) == "ERROR":
                raise Exception(job.status.details)
            elif job.status.State.Name(job.status.state) == "DONE":
                print("Job finished.")
                return job

            # Need to sleep a little or else we'll eat all the CPU
            time.sleep(0.1)
