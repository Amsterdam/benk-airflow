from datetime import datetime

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import V1EnvVar

from benk.common import NAMESPACE, TEAM_NAME
from benk.image import Image


image = Image(
    name="{{ var.value.get('pod-iburgerzaken-image-name', 'iburgerzaken_sync_image') }}",
    tag="{{ var.value.get('pod-iburgerzaken-image-tag', 'latest') }}"
)

operator_default_args = {
    "labels": {"team_name": TEAM_NAME},
    "in_cluster": True,
    "get_logs": True,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "reattach_on_restart": False,
    "do_xcom_push": False,
}

BaseOperaterArgs = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "email": ["ois.gob@amsterdam.nl"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
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

        env_vars=[
            V1EnvVar("DB_IBURGERZAKEN_SERVER", "{{ var.value.get('db-iburgerzaken-server') }}"),
            V1EnvVar("SFTP_IBURGERZAKEN_UID", "{{ var.value.get('sftp-iburgerzaken-uid') }}"),
            V1EnvVar("SFTP_IBURGERZAKEN_UID_PWD", "{{ var.value.get('sftp-iburgerzaken-uid-pwd') }}"),
            V1EnvVar("GOB_OBJECTSTORE_TENANTID", "{{ var.value.get('objectstore-gob-tenantid') }}"),
            V1EnvVar("GOB_OBJECTSTORE_USER", "{{ var.value.get('objectstore-gob-user') }}"),
            V1EnvVar("GOB_OBJECTSTORE_PWD", "{{ var.value.get('objectstore-gob-password') }}"),
        ],
        **operator_default_args,
    )

    task1
