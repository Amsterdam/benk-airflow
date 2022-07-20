import textwrap

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator

from benk.bag.common import default_args

team_name = "BenK"
workload_name = "NAP"
dag_id = team_name + "_" + workload_name

# Namespace is something like 'airflow-benkbbn1' on the actual server
namespace = Variable.get("AIRFLOW_POD_NAMESPACE", "airflow")

# Configure CONTAINER_REGISTRY_URL in the GUI
# http://localhost:8080/variable/list/
container_registry_url = Variable.get("CONTAINER_REGISTRY_URL", None)

# https://kubernetes.io/docs/concepts/containers/images/
# image_pull_policy: "Never", "Always", "IfNotPresent"
container_image = "gob-import_gobimport:latest"
if container_registry_url is None:
    # 'Never' prevents importing from a remote repository.
    image_pull_policy = "Never"
else:
    # Should be Always when pulling images from "real" registry.
    image_pull_policy = "Always"
    container_image = f"{container_registry_url}/gobimport_test:latest"

print(f"Using {container_image}")

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
        image_pull_policy=image_pull_policy,
        get_logs=True,
        hostnetwork=True,
        in_cluster=True,
        dag=dag,
        log_events_on_failure=True,
        # image_pull_secrets=[V1LocalObjectReference('regcred')],
        # configmaps=["benks-map"],
        env_vars={"CONTAINER_REGISTRY_URL": "{{ var.value.CONTAINER_REGISTRY_URL }}"},
        # secrets=[] # Secrets()
    )

nap_import
