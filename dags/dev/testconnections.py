from datetime import datetime

from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator

from socket import create_connection, timeout

with DAG(
    dag_id="testconnections",
    tags=["test", "development"],
    schedule_interval=None,
    catchup=False,
    start_date=datetime.utcnow(),
    params={
        "ip_address": Param(type="string", default="0.0.0.0"),
        "port": Param(type="integer", default=80),
    }
):

    def func(ip_address: str, port: int):
        location = (ip_address, port)
        try:
            create_connection(location, timeout=5)
            print(location, "Open :)")
        except (TimeoutError, timeout):
            print(location, "Closed :(")

    op = PythonOperator(task_id="test", python_callable=func, op_args=[
        "{{ params.ip_address }}",
        "{{ params.port }}",
    ])
