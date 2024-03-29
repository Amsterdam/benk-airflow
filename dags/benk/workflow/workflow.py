from abc import abstractmethod
from typing import Any, Mapping

from airflow.models import BaseOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

from benk.common import AKS_NODE_POOL, NAMESPACE, TEAM_NAME
from benk.environment import ImportServiceEnvironment, PrepareServiceEnvironment, UploadServiceEnvironment
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
    "is_delete_operator_pod": True,
    "startup_timeout_seconds": 240,  # twice default
    # Select a specific nodepool to use. Could also be specified by nodeAffinity.
    # Make sure we are running on workers in our namespace
    # specifying namespace parameter is not sufficient
    "node_selector": {"nodetype": AKS_NODE_POOL},
}

# Volumes are NOT templated, hardcode the values
GobVolume = Volume(
    name="gob-volume",
    mount_path="/app/shared",
    claim="benk-benkbbn1-sa-pvc",
)

UploadImage = Image(
    name="{{ var.value.get('pod-gob-upload-image-name', 'gob_upload') }}",
    tag="{{ var.value.get('pod-gob-upload-image-tag', 'latest') }}",
)

ImportImage = Image(
    name="{{ var.value.get('pod-gob-import-image-name', 'gob_import') }}",
    tag="{{ var.value.get('pod-gob-import-image-tag', 'latest') }}",
)

PrepareImage = Image(
    name="{{ var.value.get('pod-gob-prepare-image-name', 'gob_prepare') }}",
    tag="{{ var.value.get('pod-gob-prepare-image-tag', 'latest') }}",
)

# TODO: use some kind of model/pydantic
PrepareArgs: Mapping[str, Any] = dict(
    namespace=NAMESPACE,
    image=PrepareImage.url,
    image_pull_policy=PrepareImage.pull_policy,
    cmds=["python", "-m", "gobprepare"],
    env_vars=PrepareServiceEnvironment().env_vars(),
    **operator_default_args,
)

UploadArgs: Mapping[str, Any] = dict(
    namespace=NAMESPACE,
    image=UploadImage.url,
    image_pull_policy=UploadImage.pull_policy,
    volumes=[GobVolume.v1volume],
    volume_mounts=[GobVolume.v1mount],
    cmds=["python", "-m", "gobupload"],
    env_vars=UploadServiceEnvironment().env_vars(),
    **operator_default_args,
)

ImportArgs: Mapping[str, Any] = dict(
    namespace=NAMESPACE,
    image=ImportImage.url,
    image_pull_policy=ImportImage.pull_policy,
    volumes=[GobVolume.v1volume],
    volume_mounts=[GobVolume.v1mount],
    cmds=["python", "-m", "gobimport"],
    env_vars=ImportServiceEnvironment().env_vars(),
    **operator_default_args,
)


class XCom:
    """
    Class containing XCom logic.

    Pass XCOM_MESSAGE_DATA_TEMPLATE to a templated Operator field and use XCOM_PARAM_KEY in params field.
    """

    _PARAM_KEY = "xcom_task_id"
    _TEMPLATE = "{{ json.dumps(task_instance.xcom_pull('{}'.format(params.xcom_task_id))) }}"

    @classmethod
    def get_param(cls, task_id: str) -> dict[str, str]:
        """Return dict to be used in params argument of an operator."""
        return {cls._PARAM_KEY: task_id}

    @classmethod
    def get_template(cls) -> str:
        """
        Return template to be used in a templated argument of an operator.

        Examples: params, arguments, cmd
        """
        return cls._TEMPLATE


class BaseDAG:
    """Base DAG abstraction."""

    Operator = KubernetesPodOperator

    @abstractmethod
    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the last nodes in this DAG. Used to link this DAG to other DAGs."""
        pass  # pragma: no cover

    @abstractmethod
    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def id(self) -> str:
        """Return Id of the implemented DAG."""
        pass  # pragma: no cover

    def get_taskid(self, name: str) -> str:
        """Return task_id based on id and name."""
        return f"{self.id}-{name}"
