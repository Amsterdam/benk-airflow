"""Dag which imports NAP.

Order of tasks is as it was defined in gob. See gobworkflow/workflow/config.py.
"""
import json

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from kubernetes.client import V1VolumeMount, V1Volume, \
    V1PersistentVolumeClaimVolumeSource

from benk.nap.common import default_args, get_image_url, get_image_pull_policy
from benk.environment import GrondslagEnvironment, GOBEnvironment, GenericEnvironment

team_name = "BenK"
workload_name = "NAP"
dag_id = team_name + "_" + workload_name

# Variables below should be added in the GUI (http://localhost:8080/variable/list/),
# or leave empty to use defaults when available.

# The Kubernetes namespace, something like 'airflow-benkbbn1' on the server.
namespace = Variable.get("AIRFLOW_POD_NAMESPACE", default_var="airflow")
# URL to registry, leave empty to use local registry (development environment).
container_registry_url = Variable.get("CONTAINER_REGISTRY_URL", default_var=None)
image_pull_policy = get_image_pull_policy(registry_url=container_registry_url)

import_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("GOB_IMPORT_IMAGE_NAME", default_var="gob_import"),
    # In accept or test environments, different tags could be used.
    # For example :develop or :test
    tag=Variable.get("GOB_IMPORT_IMAGE_TAG", default_var="latest")
)


upload_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("GOB_UPLOAD_IMAGE_NAME", default_var="gob_upload"),
    # In accept or test environments, different tags could be used.
    # For example :develop or :test
    tag=Variable.get("GOB_UPLOAD_IMAGE_TAG", default_var="latest")
)


# Where the "gob-volume"-volume is mounted in the pod.
volume_mount = V1VolumeMount(
    name='gob-volume', mount_path='/app/shared', sub_path=None, read_only=False
)

# Which claim gob-volume should use (my-claim)
volume = V1Volume(
    name='gob-volume',
    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(claim_name='my-claim'),
)

dag_default_args = {
    "labels": {"team_name": team_name},
    "in_cluster": True,
    "get_logs": True,
    "arguments": [],
    "image_pull_policy": image_pull_policy,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "do_xcom_push": True,
    "volumes": [volume],
    "volume_mounts": [volume_mount]
}

with DAG(
    dag_id,
    default_args={**default_args, **dag_default_args},
    template_searchpath=["/"],
    user_defined_macros={
        "json": json
    }
) as dag:
    nap_import = KubernetesPodOperator(
        dag=dag,
        # task_id=f"{workload_name}-import",
        task_id=f"nap_import",
        namespace=namespace,
        image=import_container_image,
        # name=f"{workload_name}-import",
        name=f"nap_import",
        cmds=[
            "python",
            "-m",
            "gobimport",
            "import",
            "nap",
            "peilmerken",
        ],
        env_vars=GenericEnvironment().env_vars() + GrondslagEnvironment().env_vars(),
    )

    # Are these generic tasks?
    # When the current registration is not specified they are.
    # In that case make it a separate dag and link it with TriggerDagRunOperator.
    update_model = KubernetesPodOperator(
        dag=dag,
        task_id=f"update_model",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-update_model",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "apply",
            "--message-data",
            # convert dict back to json
            "{{ json.dumps(task_instance.xcom_pull('nap_import')) }}"
        ],
        env_vars=GenericEnvironment().env_vars()
    )

    import_compare = KubernetesPodOperator(
        dag=dag,
        task_id=f"import_compare",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-import_compare",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "compare",
            "--message_data",
            # convert dict back to json
            "{{ json.dumps(task_instance.xcom_pull('update_model')) }}"
        ],
        env_vars=GenericEnvironment().env_vars()
    )

    import_upload = KubernetesPodOperator(
        dag=dag,
        task_id=f"import_upload",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-import_upload",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "full_update",
            "--message_data",
            "{{ json.dumps(task_instance.xcom_pull('import_compare')) }}"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars()
    )

    apply_events = KubernetesPodOperator(
        dag=dag,
        task_id=f"apply_events",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-apply_events",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "apply",
            "--message_data",
            "{{ json.dumps(task_instance.xcom_pull('import_upload')) }}"
        ],
        env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    )

nap_import >> update_model >> import_compare >> import_upload >> apply_events
