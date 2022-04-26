from airflow import DAG
from airflow.operators.bash import BashOperator
from benk.fase_0.common import default_args

team_name = "benk"
workload_name = "fase-0-try-out"
dag_id = team_name + "_" + workload_name

with DAG(
    dag_id,
    default_args=default_args,
    template_searchpath=["/"],
) as dag:
    task1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )
    task2 = BashOperator(
        task_id="print_uptime",
        bash_command="uptime",
    )

(task1 >> task2)
