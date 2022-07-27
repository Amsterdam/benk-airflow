import textwrap

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

from benk.nap.common import default_args, get_image_url, get_image_pull_policy
from benk.settings import Settings

team_name = "BenK"
workload_name = "NAP"
dag_id = team_name + "_" + workload_name

# Variables below in the GUI (http://localhost:8080/variable/list/), or leave
# empty to use defaults.

# The Kubernetes namespace, something like 'airflow-benkbbn1' on the server.
namespace = Variable.get("AIRFLOW_POD_NAMESPACE", default_var="airflow")
# URL to registry, leave empty to use local registry (development environment).
container_registry_url = Variable.get("CONTAINER_REGISTRY_URL", default_var=None)
image_name = Variable.get("GOB_IMPORT_IMAGE_NAME", default_var="gob_import")
# In accept or test environments, different tags could be used. For example:
# :develop or :test
tag = Variable.get("GOB_IMPORT_IMAGE_TAG", default_var="latest")

container_image = get_image_url(
    registry_url=container_registry_url, image_name=image_name, tag=tag
)
image_pull_policy = get_image_pull_policy(registry_url=container_registry_url)
settings = Settings()

with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    nap_import = KubernetesPodOperator(
        dag=dag,
        task_id=f"{workload_name}-import",
        namespace=namespace,
        image=container_image,
        name=f"{workload_name}-import",
        cmds=[
            "python",
            "-m",
            "gobimport",
            "import",
            "--xcom_data",
            "{{ task_instance.xcom_pull('write-xcom') }}",
            "nap",
            "peilmerken",
        ],
        env_vars=settings.env_vars(),
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

nap_import
