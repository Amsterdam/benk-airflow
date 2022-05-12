from airflow import DAG
from airflow.operators.bash import BashOperator

from benk.bag.common import default_args

team_name = "BenK"
workload_name = "BAG"
dag_id = team_name + "_" + workload_name

with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
    schedule_interval="0 0 * * *"
) as dag:
    bag_extract = BashOperator(
        task_id="BAG_extract_neuron",
        bash_command='echo "Running bag extract..."',
        dag=dag,
    )
    bag_transform = BashOperator(
        task_id="BAG_transform_to_amsterdam_schema",
        bash_command='echo "Running bag transform..."',
        dag=dag,
    )
    bag_load = BashOperator(
        task_id="BAG_load_to_referentie_db",
        bash_command='echo "Running bag load..."',
        dag=dag,
    )

(bag_extract >> bag_transform >> bag_load)
