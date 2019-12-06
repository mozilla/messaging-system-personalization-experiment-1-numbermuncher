from google.cloud.dataproc_v1.gapic.transports import cluster_controller_grpc_transport
from google.cloud import dataproc_v1

waiting_callback = False


def cluster_callback(operation_future):
    # Reset global when callback returns.
    global waiting_callback
    waiting_callback = False


def get_region_from_zone(zone):
    try:
        region_as_list = zone.split("-")[:-1]
        return "-".join(region_as_list)
    except (AttributeError, IndexError, ValueError):
        raise ValueError("Invalid zone provided, please check your input.")


def dataproc_cluster_client(zone):
    """
    Lazily create a Dataproc ClusterController client to setup or
    tear down dataproc clusters
    """
    region = get_region_from_zone(zone)

    client_transport = cluster_controller_grpc_transport.ClusterControllerGrpcTransport(
        address="{}-dataproc.googleapis.com:443".format(region)
    )
    return dataproc_v1.ClusterControllerClient(client_transport)


def create_cluster(cluster_name, project_id, zone):
    """Create the cluster."""

    # TODO: pass in the bucket somehow. maybe an attribute
    # settings
    # bucket_name = "cfr-ml-jobs"

    print("Creating cluster...")
    cluster_config = {
        "cluster_name": cluster_name,
        "project_id": project_id,
        "config": {
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
                "policy_uri": "projects/cfr-personalization-experiment/regions/us-west1/autoscalingPolicies/cfr-personalization-autoscale"
            },
            "initialization_actions": [
                {
                    "executable_file": "gs://cfr-ml-jobs/actions/python/dataproc_custom.sh"
                }
            ],
            "software_config": {"image_version": "1.4.16-ubuntu18"},
        },
    }

    cluster = dataproc_cluster_client(zone).create_cluster(
        project_id, get_region_from_zone(zone), cluster_config
    )
    cluster.add_done_callback(cluster_callback)
    global waiting_callback
    waiting_callback = True


def wait_for_cluster_creation():
    """Wait for cluster creation."""
    print("Waiting for cluster creation...")

    while True:
        if not waiting_callback:
            print("Cluster created.")
            break


if __name__ == "__main__":
    cluster_name = "cfr-demo-cluster-py3"
    project_id = "cfr-personalization-experiment"
    zone = "us-west1-a"
    create_cluster(cluster_name, project_id, zone)
    wait_for_cluster_creation()
