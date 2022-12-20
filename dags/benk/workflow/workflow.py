from abc import abstractmethod

from airflow.models import BaseOperator, Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

from benk.common import NAMESPACE, TEAM_NAME
from benk.environment import (
    DGDialogEnvironment,
    GenericEnvironment,
    GOBEnvironment,
    GOBPrepareDatabaseEnvironment,
    GrondslagEnvironment,
    NeuronDatabaseEnvironment,
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

PrepareImage = Image(
    name=Variable.get("pod-gob-prepare-image-name", default_var="gob_prepare"),
    tag=Variable.get("pod-gob-prepare-image-tag", default_var="latest")
)

PrepareArgs = dict(
    namespace=NAMESPACE,
    image=PrepareImage.url,
    image_pull_policy=PrepareImage.pull_policy,
    cmds=["python", "-m", "gobprepare"],
    env_vars=NeuronDatabaseEnvironment().env_vars() + GOBPrepareDatabaseEnvironment().env_vars(),
    **operator_default_args,
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
    """Base DAG abstraction."""

    Operator: KubernetesPodOperator = KubernetesPodOperator

    @abstractmethod
    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the last nodes in this DAG. Used to link this DAG to other DAGs."""
        pass  # pragma: no cover

    @abstractmethod
    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        pass  # pragma: no cover
