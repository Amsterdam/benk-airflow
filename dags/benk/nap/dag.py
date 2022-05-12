from airflow import DAG
from airflow.operators.bash import BashOperator

from benk.bag.common import default_args

team_name = "BenK"
workload_name = "BAG"
dag_id = team_name + "_" + workload_name
# TODO: Figure out in which environment this dag is running,
#  or set an env var with the container_image url in the airflow UI.
# container_image = "benkontacr.azurecr.io/benk-airflow-task:development"
# command = ["/bin/sh", "-c", "/app/entrypoint.sh"]

BashOperator

with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    bag_extract = BashOperator(
        task_id="BAG_extract_neuron",
        bash_command='echo "Running bag extract..."',
        namespace="airflow-benkbbn1",
        # arguments=arguments,
        labels={"team_name": team_name},
        name=workload_name,
        dag=dag,
        log_events_on_failure=True
    )
    bag_transform = BashOperator(
        task_id="BAG_transform_to_amsterdam_schema",
        bash_command='echo "Running bag transform..."',
        namespace="airflow-benkbbn1",
        # arguments=arguments,
        labels={"team_name": team_name},
        name=workload_name,
        dag=dag,
        log_events_on_failure=True
    )
    bag_load = BashOperator(
        task_id="BAG_load_to_referentie_db",
        bash_command='echo "Running bag load..."',
        namespace="airflow-benkbbn1",
        # arguments=arguments,
        labels={"team_name": team_name},
        name=workload_name,
        dag=dag,
        log_events_on_failure=True
    )

(bag_extract >> bag_transform >> bag_load)
