from datetime import datetime
from typing import Any

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

from benk.common import NAMESPACE, TEAM_NAME, BaseOperaterArgs
from benk.environment import IburgerZakenEnvironment
from benk.image import Image

image = Image(
    name="{{ var.value.get('pod-iburgerzaken-image-name', 'iburgerzaken-sftp-sync') }}",
    tag="{{ var.value.get('pod-iburgerzaken-image-tag', 'latest') }}",
)

operator_default_args: dict[str, Any] = {
    "labels": {"team_name": TEAM_NAME},
    "in_cluster": True,
    "get_logs": True,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "reattach_on_restart": False,
    "do_xcom_push": False,
}

with DAG(
    dag_id="iburgerzaken",
    tags=["pink", "brp"],
    default_args=BaseOperaterArgs,
    catchup=False,
    start_date=datetime.utcnow(),
    params={"operation": "sync", "destination": "development/iburgerzaken"},
):
    execute_task = KubernetesPodOperator(
        name="execute",
        task_id="execute",
        namespace=NAMESPACE,
        image=image.url,
        image_pull_policy=image.pull_policy,
        cmds=["python3"],
        arguments=["main.py", "{{ params.operation }}", "{{ params.destination }}"],
        env_vars=IburgerZakenEnvironment().env_vars(),
        **operator_default_args,
    )

    execute_task
