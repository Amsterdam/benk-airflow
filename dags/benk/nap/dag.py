import textwrap

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator

from benk.bag.common import default_args

team_name = "BenK"
workload_name = "NAP"
dag_id = team_name + "_" + workload_name
# Configure CONTAINER_REGISTRY_URL in the GUI
# http://localhost:8080/variable/list/
container_registry_url = Variable.get("CONTAINER_REGISTRY_URL", "")
container_image = f"{container_registry_url}/python:3.10"
namespace = "airflow"

print(f"Fetching containers from {container_registry_url}")

with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    nap_import = KubernetesPodOperator(
        task_id=f"{workload_name}-import",
        namespace=namespace,
        image=container_image,
        cmds=[
            "python", "-c", textwrap.dedent("""
            import os
            for k, v in os.environ.items():
                print(f'{k}: {v}')
            """)
        ],
        # arguments=arguments,
        labels={"team_name": team_name},
        name=f"{workload_name}-import",
        image_pull_policy="Always",
        get_logs=True,
        hostnetwork=True,
        in_cluster=True,
        dag=dag,
        log_events_on_failure=True,
        # configmaps=["benks-map"],
        env_vars={"CONTAINER_REGISTRY_URL": "{{ var.value.CONTAINER_REGISTRY_URL }}"},
        # secrets=[] # Secrets()
    )

nap_import
