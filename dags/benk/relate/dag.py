"""Dag which relates NAP peilmerken to gebieden bouwblokken.

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
from benk.environment import GOBEnvironment, GenericEnvironment

team_name = "BenK"
workload_name = "relate_NAP"
dag_id = team_name + "_" + workload_name

namespace = Variable.get("pod-namespace", default_var="airflow")
container_registry_url = Variable.get("pod-container-registry-url", default_var=None)
image_pull_policy = get_image_pull_policy(registry_url=container_registry_url)

upload_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("pod-gob-upload-image-name", default_var="gob_upload"),
    tag=Variable.get("pod-gob-upload-image-tag", default_var="latest"),
)

# Where the "gob-volume"-volume is mounted in the pod.
volume_mount = V1VolumeMount(
    name="gob-volume", mount_path="/app/shared", sub_path=None, read_only=False
)

# Which claim gob-volume should use (shared-storage-claim)
volume = V1Volume(
    name="gob-volume",
    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
        claim_name=Variable.get("pod-gob-shared-storage-claim", "shared-storage-claim")
    )
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
    tags=["relate"],
    schedule_interval=None,
    catchup=False,
    start_date=datetime.utcnow()
) as dag:

    workflow = "nap_peilmerken_ligt_in_gebieden_bouwblok"

    relate_prepare = KubernetesPodOperator(
        dag=dag,
        task_id="relate_prepare",
        namespace=namespace,
        image=upload_container_image,
        name="relate_prepare",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "relate_prepare",
            "--catalogue=nap",
            "--collection=peilmerken",
            "--attribute=ligt_in_gebieden_bouwblok",
            "--mode=full"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars()
    )

    relate_process = KubernetesPodOperator(
        dag=dag,
        task_id="relate_process",
        namespace=namespace,
        image=upload_container_image,
        name="relate_process",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('relate_prepare')) }}",
            "relate_process"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars()
    )

    import_upload = KubernetesPodOperator(
        dag=dag,
        task_id="import_upload",
        namespace=namespace,
        image=upload_container_image,
        name="import_upload",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('relate_process')) }}",
            "full_update"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

    apply_events = KubernetesPodOperator(
        dag=dag,
        task_id="apply_events",
        namespace=namespace,
        image=upload_container_image,
        name="apply_events",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('import_upload')) }}",
            "apply",
            "--catalogue=nap",
            # "--collection=peilmerken" needs to be fixed in upload (entity is used, not collection)
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

    update_view = KubernetesPodOperator(
        dag=dag,
        task_id="update_view",
        namespace=namespace,
        image=upload_container_image,
        name="update_view",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('apply_events')) }}",
            "relate_update_view"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

    relate_check = KubernetesPodOperator(
        dag=dag,
        task_id="relate_check",
        namespace=namespace,
        image=upload_container_image,
        name="relate_check",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('update_view')) }}",
            "relate_check"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

relate_prepare >> relate_process >> import_upload >> apply_events >> update_view >> relate_check
