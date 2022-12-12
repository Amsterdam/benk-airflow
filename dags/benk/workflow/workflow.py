from abc import abstractmethod

from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from benk.common import NAMESPACE, TEAM_NAME
from benk.environment import (
    DGDialogEnvironment,
    GenericEnvironment,
    GOBEnvironment,
    GrondslagEnvironment,
    ObjectStoreBasisInformatieEnvironment,
)
from benk.image import Image
from benk.volume import Volume


operator_default_args = {
    "labels": {"team_name": TEAM_NAME},
    "in_cluster": True,
    "get_logs": True,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "reattach_on_restart": False,
    "do_xcom_push": True,
}

GobVolume = Volume(
    name="gob-volume",
    mount_path="/app/shared",
    claim=Variable.get("pod-gob-shared-storage-claim", "shared-storage-claim"),
)


UploadImage = Image(
    name=Variable.get("pod-gob-upload-image-name", default_var="gob_upload"),
    tag=Variable.get("pod-gob-upload-image-tag", default_var="latest"),
)

ImportImage = Image(
    name=Variable.get("pod-gob-import-image-name", default_var="gob_import"),
    tag=Variable.get("pod-gob-import-image-tag", default_var="latest"),
)

UploadArgs = dict(
    namespace=NAMESPACE,
    image=UploadImage.url,
    image_pull_policy=UploadImage.pull_policy,
    volumes=[GobVolume.v1volume],
    volume_mounts=[GobVolume.v1mount],
    cmds=["python", "-m", "gobupload"],
    env_vars=GenericEnvironment().env_vars() + GOBEnvironment().env_vars(),
    **operator_default_args,
)

# TODO: filter env vars per import
# TODO: store as secret?
# TODO: Use templates!
# https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#airflow-variables
ImportArgs = dict(
    namespace=NAMESPACE,
    image=ImportImage.url,
    image_pull_policy=ImportImage.pull_policy,
    volumes=[GobVolume.v1volume],
    volume_mounts=[GobVolume.v1mount],
    cmds=["python", "-m", "gobimport"],
    env_vars=(
        GenericEnvironment().env_vars()
        + GrondslagEnvironment().env_vars()
        + DGDialogEnvironment().env_vars()
        + ObjectStoreBasisInformatieEnvironment().env_vars()
    ),
    **operator_default_args,
)


class BaseDAG:

    Operator = KubernetesPodOperator

    @classmethod
    @abstractmethod
    def tasks(cls):  # pragma: no cover
        pass


class Import(BaseDAG):
    @classmethod
    def import_(cls):
        return cls.Operator(
            task_id="import",
            name="import",  # required
            arguments=[
                "import",
                "--catalogue={{ params.catalogue }}",
                "--collection={{ params.collection }}",
                "--application={{ params.application }}",
                "--mode={{ params.mode }}",
            ],
            **ImportArgs,
        )

    @classmethod
    def update(cls):
        return cls.Operator(
            task_id="update",
            name="update",
            arguments=[
                "apply",
                "--catalogue={{ params.catalogue }}",
                "--collection={{ params.collection }}",
            ],
            **UploadArgs,
        )

    @classmethod
    def compare(cls):
        return cls.Operator(
            task_id="compare",
            name="compare",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('import')) }}",
                "compare",
            ],
            **UploadArgs,
        )

    @classmethod
    def upload(cls):
        return cls.Operator(
            task_id="upload",
            name="upload",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('compare')) }}",
                "full_update",
            ],
            **UploadArgs,
        )

    @classmethod
    def apply(cls):
        return cls.Operator(
            task_id="apply",
            name="apply",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('upload')) }}",
                "apply",
            ],
            **UploadArgs,
        )

    @classmethod
    def tasks(cls):
        return [
            cls.import_(),
            cls.update(),
            cls.compare(),
            cls.upload(),
            cls.apply()
        ]


class Relate(BaseDAG):
    @classmethod
    def prepare(cls):
        return cls.Operator(
            task_id="prepare",
            name="prepare",
            arguments=[
                "relate_prepare",
                "--catalogue={{ params.catalogue }}",
                "--collection={{ params.collection }}",
                "--attribute={{ params.attribute }}",
                "--mode=full",
            ],
            **UploadArgs,
        )

    @classmethod
    def process(cls):
        return cls.Operator(
            task_id="process",
            name="process",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('prepare')) }}",
                "relate_process",
            ],
            **UploadArgs,
        )

    @classmethod
    def update(cls):
        return cls.Operator(
            task_id="update",
            name="update",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('process')) }}",
                "full_update",
            ],
            **UploadArgs,
        )

    @classmethod
    def apply(cls):
        return cls.Operator(
            task_id="apply",
            name="apply",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('update')) }}",
                "apply",
            ],
            **UploadArgs,
        )

    @classmethod
    def update_view(cls):
        return cls.Operator(
            task_id="update_view",
            name="update_view",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('apply')) }}",
                "relate_update_view",
            ],
            **UploadArgs,
        )

    @classmethod
    def check(cls):
        return cls.Operator(
            task_id="check",
            name="check",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('update_view')) }}",
                "relate_check",
            ],
            **UploadArgs,
        )

    @classmethod
    def tasks(cls):
        return [
            cls.prepare(),
            cls.process(),
            cls.update(),
            cls.apply(),
            cls.update_view(),
            cls.check()
        ]
