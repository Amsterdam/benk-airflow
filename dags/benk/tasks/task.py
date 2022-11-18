from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from benk.common import NAMESPACE, TEAM_NAME
from benk.environment import GenericEnvironment, GOBEnvironment
from benk.image import UploadImage, ImportImage
from benk.volume import GobVolume


operator_default_args = {
    "labels": {"team_name": TEAM_NAME},
    "in_cluster": True,
    "get_logs": True,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "reattach_on_restart": False,
    "do_xcom_push": True,
}


class UploadOperator(KubernetesPodOperator):

    image = UploadImage
    volume = GobVolume

    def __init__(self, task_id: str, **kwargs):
        super().__init__(
            task_id=task_id,
            namespace=NAMESPACE,
            image=self.image.url,
            name=self.task_id,
            image_pull_policy=self.image.pull_policy,
            volumes=[self.volume.v1volume],
            volume_mounts=[self.volume.v1mount],
            entrypoint=["python", "-m", "gobupload"],
            env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
            **operator_default_args,
            **kwargs
        )


class ImportOperator(KubernetesPodOperator):

    image = ImportImage
    volume = GobVolume

    def __init__(self, task_id: str, **kwargs):
        super().__init__(
            task_id=task_id,
            namespace=NAMESPACE,
            image=self.image.url,
            name=self.task_id,
            image_pull_policy=self.image.pull_policy,
            volumes=[self.volume.v1volume],
            volume_mounts=[self.volume.v1mount],
            entrypoint=["python", "-m", "gobimport"],
            env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
            **operator_default_args,
            **kwargs
        )
