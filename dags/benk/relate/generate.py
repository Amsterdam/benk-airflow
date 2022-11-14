import json
from datetime import datetime
from functools import cache
from pathlib import Path

from airflow.models.dag import DAG

from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from kubernetes.client import (
    V1VolumeMount,
    V1Volume,
    V1PersistentVolumeClaimVolumeSource,
)
#
from benk.common import default_args, get_image_url, get_image_pull_policy
from benk.environment import GOBEnvironment, GenericEnvironment

team_name = "BenK"

container_registry_url = Variable.get("pod-container-registry-url", default_var=None)
image_pull_policy = get_image_pull_policy(registry_url=container_registry_url)

upload_container_image = get_image_url(
    registry_url=container_registry_url,
    image_name=Variable.get("pod-gob-upload-image-name", default_var="gob_upload"),
    tag=Variable.get("pod-gob-upload-image-tag", default_var="latest"),
)

# Where the "gob-volume"-volume is mounted in the pod.
volume_mount = V1VolumeMount(
    name="gob-volume", mount_path="/app/shared", sub_path=None, read_only=False
)

# Which claim gob-volume should use (shared-storage-claim)
volume = V1Volume(
    name="gob-volume",
    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
        claim_name=Variable.get("pod-gob-shared-storage-claim", "shared-storage-claim")
    )
)


class Tasks:

    Operator = KubernetesPodOperator

    namespace = Variable.get("pod-namespace", default_var="airflow")
    entrypoint = ["python", "-m", "gobupload"]
    env_vars = GenericEnvironment().env_vars() + GOBEnvironment().env_vars()

    operator_default_args = {
        "labels": {"team_name": team_name},
        "in_cluster": True,
        "get_logs": True,
        "image_pull_policy": image_pull_policy,
        "hostnetwork": True,
        "log_events_on_failure": True,
        "reattach_on_restart": False,
        "do_xcom_push": True,
        "volumes": [volume],
        "volume_mounts": [volume_mount]
    }

    @classmethod
    def relate_prepare(cls):
        return cls.Operator(
            task_id="relate_prepare",
            namespace=cls.namespace,
            # image=(
            #     "{{ var.value.pod-container-registry-url }}"
            #     "/{{ var.value.pod-gob-upload-image-name }}"
            #     ":{{ var.value.pod-gob-upload-image-tag }}"
            # ),
            image=upload_container_image,
            name="relate_prepare",
            cmds=cls.entrypoint,
            arguments=[
                "relate_prepare",
                "--catalogue={{ params.catalog }}",
                "--collection={{ params.collection }}",
                "--attribute={{ params.relation }}",
                "--mode=full"
            ],
            env_vars=cls.env_vars,
            **cls.operator_default_args
        )

    @classmethod
    def relate_process(cls):
        return cls.Operator(
            task_id="relate_process",
            namespace=cls.namespace,
            # image=(
            #     "{{ var.value.pod-container-registry-url }}"
            #     "/{{ var.value.pod-gob-upload-image-name }}"
            #     ":{{ var.value.pod-gob-upload-image-tag }}"
            # ),
            image=upload_container_image,
            name="relate_process",
            cmds=cls.entrypoint,
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('relate_prepare')) }}",
                "relate_process"
            ],
            env_vars=cls.env_vars,
            **cls.operator_default_args
        )

    @classmethod
    def import_upload(cls):
        return cls.Operator(
            task_id="import_upload",
            namespace=cls.namespace,
            # image=(
            #     "{{ var.value.pod-container-registry-url }}"
            #     "/{{ var.value.pod-gob-upload-image-name }}"
            #     ":{{ var.value.pod-gob-upload-image-tag }}"
            # ),
            image=upload_container_image,
            name="import_upload",
            cmds=cls.entrypoint,
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('relate_process')) }}",
                "full_update"
            ],
            env_vars=cls.env_vars,
            **cls.operator_default_args
        )

    @classmethod
    def apply_events(cls):
        return cls.Operator(
            task_id="apply_events",
            namespace=cls.namespace,
            # image=(
            #     "{{ var.value.pod-container-registry-url }}"
            #     "/{{ var.value.pod-gob-import-image-name }}"
            #     ":{{ var.value.pod-gob-import-image-tag }}"
            # ),
            image=upload_container_image,
            name="apply_events",
            cmds=cls.entrypoint,
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('import_upload')) }}",
                "apply"
            ],
            env_vars=cls.env_vars,
            **cls.operator_default_args
        )

    @classmethod
    def update_view(cls):
        return cls.Operator(
            task_id="update_view",
            namespace=cls.namespace,
            # image=(
            #     "{{ var.value.pod-container-registry-url }}"
            #     "/{{ var.value.pod-gob-import-image-name }}"
            #     ":{{ var.value.pod-gob-import-image-tag }}"
            # ),
            image=upload_container_image,
            name="update_view",
            cmds=cls.entrypoint,
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('apply_events')) }}",
                "relate_update_view"
            ],
            env_vars=cls.env_vars,
            **cls.operator_default_args
        )

    @classmethod
    def relate_check(cls):
        return cls.Operator(
            task_id="relate_check",
            namespace=cls.namespace,
            # image=(
            #     "{{ var.value.pod-container-registry-url }}"
            #     "/{{ var.value.pod-gob-import-image-name }}"
            #     ":{{ var.value.pod-gob-import-image-tag }}"
            # ),
            image=upload_container_image,
            name="relate_check",
            cmds=cls.entrypoint,
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('update_view')) }}",
                "relate_check"
            ],
            env_vars=cls.env_vars,
            **cls.operator_default_args
        )


@cache
def get_relations():
    # depends on local gobmodel.json
    with open(Path(__file__).parent.parent / "gobmodel.json", encoding="utf-8") as fp:
        gobmodel = json.load(fp)

    return {
        catalog: {
            collection_name:
                [attr for attr, value in attributes.get("attributes", {}).items() if "Reference" in value["type"]] +
                [attr for attr, value in attributes.get("legacy_attributes", {}).items() if
                 "Reference" in value["type"]]
            for collection_name, attributes in collections["collections"].items()
        }
        for catalog, collections in gobmodel.items()
        if catalog not in {"test_catalogue", "brp", "wkpb", "hr", "brk2", "qa", "rel"}
    }


dag_default_args = {
    "default_args": default_args,
    "template_searchpath": ["/"],
    "user_defined_macros": {"json": json},
    "schedule_interval": None,
    "catchup": False,
    "start_date": datetime.utcnow()
}


for catalog, collections in get_relations().items():
    for collection, relations in collections.items():
        for relation in relations:

            params = {
                "catalog": catalog,
                "collection": collection,
                "relation": relation
            }

            with DAG(
                dag_id=f"{catalog}_{collection}_{relation}",
                params=params,
                tags=["relate", catalog, collection, relation],
                **dag_default_args
            ):
                (
                    Tasks.relate_prepare() >>
                    Tasks.relate_process() >>
                    Tasks.import_upload() >>
                    Tasks.apply_events() >>
                    Tasks.update_view() >>
                    Tasks.relate_check()
                )
