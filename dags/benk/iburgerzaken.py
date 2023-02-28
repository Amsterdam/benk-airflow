from datetime import datetime
from typing import Any

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

from benk.common import NAMESPACE, TEAM_NAME, BaseOperaterArgs
from benk.environment import IburgerZakenEnvironment
from benk.image import Image

image = Image(
    name="{{ var.value.get('pod-iburgerzaken-image-name', 'iburgerzaken_sync_image') }}",
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
):
    task1 = KubernetesPodOperator(
        name="list_contents",
        task_id="list_contents",
        namespace=NAMESPACE,
        image=image.url,
        image_pull_policy=image.pull_policy,
        cmds=["python3"],
        arguments=["main.py"],
        env_vars=IburgerZakenEnvironment().env_vars(),
        **operator_default_args,
    )

    task1
