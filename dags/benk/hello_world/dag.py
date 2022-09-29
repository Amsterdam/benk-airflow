"""Very simple dag to test infra functionality."""
import json

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from kubernetes.client import (
    V1VolumeMount,
    V1Volume,
    V1PersistentVolumeClaimVolumeSource,
)

from benk.common import default_args, get_image_url, get_image_pull_policy

team_name = "BenK"
workload_name = "Hello_World"
dag_id = team_name + "_" + workload_name

# Variables below should be added in the GUI (http://localhost:8080/variable/list/),
# or leave empty to use defaults when available.

# The Kubernetes namespace, something like 'airflow-benkbbn1' on the server.
namespace = Variable.get("AIRFLOW-POD-NAMESPACE", default_var="airflow")
# URL to registry, leave empty to use local registry (development environment).
container_registry_url = Variable.get("CONTAINER-REGISTRY-URL", default_var=None)
image_pull_policy = get_image_pull_policy(registry_url=container_registry_url)

import_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("GOB-IMPORT-IMAGE-NAME", default_var="gob_import"),
    # In accept or test environments, different tags could be used.
    # For example :develop or :test
    tag=Variable.get("GOB-IMPORT-IMAGE-TAG", default_var="latest"),
)


# Where the "gob-volume"-volume is mounted in the pod.
volume_mount = V1VolumeMount(
    name="gob-volume", mount_path="/app/shared", sub_path=None, read_only=False
)

# Which claim gob-volume should use (shared-storage-claim)
volume = V1Volume(
    name="gob-volume",
    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
        claim_name=Variable.get("GOB-SHARED-STORAGE-CLAIM", "shared-storage-claim")
    ),
)

dag_default_args = {
    "labels": {"team_name": team_name},
    "in_cluster": True,
    "get_logs": True,
    "arguments": [],
    "image_pull_policy": image_pull_policy,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "volumes": [volume],
    "volume_mounts": [volume_mount],
}

with DAG(
    dag_id,
    default_args={**default_args, **dag_default_args},
    template_searchpath=["/"],
    user_defined_macros={"json": json},
) as dag:
    hello_world = KubernetesPodOperator(
        dag=dag,
        task_id=f"hello_world",
        namespace=namespace,
        image=import_container_image,
        name=f"hello_world",
        cmds=["echo", "Hello world!"],
    )

hello_world
