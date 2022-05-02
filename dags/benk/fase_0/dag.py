from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator

from benk.fase_0.common import default_args

team_name = "benk"
workload_name = "fase-0-try-out"
dag_id = team_name + "_" + workload_name

container_image = "benkontacr.azurecr.io/test-image:latest"
command = ["/bin/sh", "-c", "/app/entrypoint.sh"]


with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    task2 = KubernetesPodOperator(
        task_id="container_test",
        # namespace=os.getenv("AIRFLOW__KUBERNETES__NAMESPACE", "default"),
        namespace="airflow-benkbbn1",
        image=container_image,
        cmds=command,
        # arguments=arguments,
        labels={"team_name": team_name},
        name=workload_name,
        image_pull_policy="Always",
        get_logs=True,
        in_cluster=True,
        dag=dag,
        log_events_on_failure=True
    )
