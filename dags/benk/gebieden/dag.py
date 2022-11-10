"""Dag which imports NAP.

Order of tasks is as it was defined in gob. See gobworkflow/workflow/config.py.
"""
import json
from datetime import datetime

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
from benk.environment import GOBEnvironment, ObjectStoreBasisInformatieEnvironment, GenericEnvironment, DGDialogEnvironment

team_name = "BenK"
workload_name = "GEBIEDEN"
dag_id = team_name + "_" + workload_name


namespace = Variable.get("pod-namespace")
container_registry_url = Variable.get("pod-container-registry-url", None)
image_pull_policy = get_image_pull_policy(registry_url=container_registry_url)

import_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("pod-gob-import-image-name"),
    tag=Variable.get("pod-gob-import-image-tag")
)


upload_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("pod-gob-upload-image-name"),
    tag=Variable.get("pod-gob-upload-image-tag"),
)


# Where the "gob-volume"-volume is mounted in the pod.
volume_mount = V1VolumeMount(
    name="gob-volume",
    mount_path="/app/shared",
    sub_path=None,
    read_only=False
)

# Which claim gob-volume should use (shared-storage-claim)
volume = V1Volume(
    name="gob-volume",
    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
        claim_name=Variable.get("pod-gob-shared-storage-claim", "shared-storage-claim")
    ),
)

operator_default_args = {
    "labels": {"team_name": team_name},
    "in_cluster": True,
    "get_logs": True,
    "arguments": [],
    "image_pull_policy": image_pull_policy,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "reattach_on_restart": False,
    "do_xcom_push": True,
    "volumes": [volume],
    "volume_mounts": [volume_mount],
}

with DAG(
    dag_id,
    default_args={**default_args, **operator_default_args},
    template_searchpath=["/"],
    user_defined_macros={"json": json},
    tags=["import", "apply", "compare"],
    schedule_interval=None,
    catchup=False,
    start_date=datetime.utcnow()
) as dag:
    gebieden_import = KubernetesPodOperator(
        dag=dag,
        task_id="gebieden_import",
        namespace=namespace,
        image=import_container_image,
        name="gebieden_import",
        cmds=[
            "python",
            "-m",
            "gobimport",
            "import",
            "--catalogue=gebieden",
            "--collection=bouwblokken",
            "--application=DGDialog",
            "--mode=full"
        ],
        env_vars=(
            GenericEnvironment().env_vars() +
            DGDialogEnvironment().env_vars() +
            ObjectStoreBasisInformatieEnvironment().env_vars()
        ),
    )

    update_model = KubernetesPodOperator(
        dag=dag,
        task_id="update_model",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-update_model",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "apply",
            "--catalogue=gebieden",
            "--collection=bouwblokken",
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

    import_compare = KubernetesPodOperator(
        dag=dag,
        task_id="import_compare",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-import_compare",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('gebieden_import')) }}",
            "compare",
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

    import_upload = KubernetesPodOperator(
        dag=dag,
        task_id="import_upload",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-import_upload",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('import_compare')) }}",
            "full_update",
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

    apply_events = KubernetesPodOperator(
        dag=dag,
        task_id="apply_events",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-apply_events",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('import_upload')) }}",
            "apply",
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

gebieden_import >> update_model >> import_compare >> import_upload >> apply_events
