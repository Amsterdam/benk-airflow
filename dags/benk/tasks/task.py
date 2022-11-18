from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from benk.common import NAMESPACE, TEAM_NAME
from benk.environment import GenericEnvironment, GOBEnvironment
from benk.image import Image, UploadImage, ImportImage
from benk.volume import GobVolume, Volume


class Task:

    Operator = KubernetesPodOperator

    operator_default_args = {
        "labels": {"team_name": TEAM_NAME},
        "in_cluster": True,
        "get_logs": True,
        "hostnetwork": True,
        "log_events_on_failure": True,
        "reattach_on_restart": False,
        "do_xcom_push": True,
    }

    def __init__(self, task_id: str, *, image: Image, volume: Volume, **kwargs):
        self.task_id = task_id
        self.image = image
        self.volume = volume
        self.task_kwargs = kwargs

    def generate(self):
        return self.Operator(
            task_id=self.task_id,
            namespace=NAMESPACE,
            image=self.image.url,
            name=self.task_id,
            image_pull_policy=self.image.pull_policy,
            volumes=[self.volume.v1volume],
            volume_mounts=[self.volume.v1mount],
            **self.operator_default_args,
            **self.task_kwargs,
        )


class UploadTask:

    @classmethod
    def run(cls, **kwargs):
        return Task(
            "upload",
            image=UploadImage,
            volume=GobVolume,
            entrypoint=["python", "-m", "gobupload"],
            env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
            **kwargs
        ).generate()


class ImportTask:

    @classmethod
    def run(cls, **kwargs):
        return Task(
            "import",
            image=ImportImage,
            volume=GobVolume,
            entrypoint=["python", "-m", "gobimport"],
            env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
            **kwargs
        ).generate()
