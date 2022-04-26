from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator

from benk.fase_0.common import default_args

team_name = "benk"
workload_name = "fase-0-try-out"
dag_id = team_name + "_" + workload_name

container_image = "benkontacr.azurecr.io/test-image:latest"
command = ["/bin/sh", "-c", "./entrypoint.sh"]


with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    task1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )
    task2 = KubernetesPodOperator(
        task_id="container_test",
        # namespace=os.getenv("AIRFLOW__KUBERNETES__NAMESPACE", "default"),
        image=container_image,
        cmds=command,
        # arguments=arguments,
        labels={"team_name": team_name},
        name=workload_name,
        image_pull_policy="Always",
        get_logs=True,
        in_cluster=True,
        dag=dag,
    )

(task1 >> task2)
