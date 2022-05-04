from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator

from benk.fase_0.common import default_args

team_name = "benk"
workload_name = "NAP_Extract"
dag_id = team_name + "_" + workload_name
# TODO: Figure out in which environment this dag is running,
#  or set an env var with the container_image url in the airflow UI.
container_image = "benkontacr.azurecr.io/benk-airflow-task:development"
command = ["/bin/sh", "-c", "/app/entrypoint.sh"]


with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    nap_extract = KubernetesPodOperator(
        task_id="NAP_extract",
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
