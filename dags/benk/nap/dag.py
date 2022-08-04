import json

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

from benk.nap.common import default_args, get_image_url, get_image_pull_policy
from benk.environment import GrondslagEnvironment

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
    # In accept or test environments, different tags could be used. For example:
    # :develop or :test
    tag=Variable.get("GOB_IMPORT_IMAGE_TAG", default_var="latest")
)


upload_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("GOB_UPLOAD_IMAGE_NAME", default_var="gob_upload"),
    # In accept or test environments, different tags could be used. For example:
    # :develop or :test
    tag=Variable.get("GOB_UPLOAD_IMAGE_TAG", default_var="latest")
)


with DAG(
    dag_id,
    default_args=default_args,
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
        env_vars=GrondslagEnvironment().env_vars(),
        labels={"team_name": team_name},
        in_cluster=True,
        get_logs=True,
        arguments=[],
        image_pull_policy=image_pull_policy,
        hostnetwork=True,
        log_events_on_failure=True,
        do_xcom_push=True,
        # secrets=[settings.secrets(]
    )
    nap_apply = KubernetesPodOperator(
        dag=dag,
        task_id=f"{workload_name}-upload",
        namespace=namespace,
        image=upload_container_image,
        name=f"{workload_name}-import",
        cmds=[
            "python",
            "-m",
            "gobupload",
            "apply",
            "--xcom-data",
            # convert dict back to json
            "{{ json.dumps(task_instance.xcom_pull('nap_import')) }}"
        ],
        env_vars=GrondslagEnvironment().env_vars(),
        labels={"team_name": team_name},
        in_cluster=True,
        get_logs=True,
        arguments=[],
        image_pull_policy=image_pull_policy,
        hostnetwork=True,
        log_events_on_failure=True,
        do_xcom_push=True,
        # secrets=[settings.secrets(]
    )

nap_import >> nap_apply
