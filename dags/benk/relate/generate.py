import json
from datetime import datetime
from functools import cache
from pathlib import Path

from airflow.models.dag import DAG

from benk.common import default_args
from benk.tasks import UploadOperator


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
                prepare = UploadOperator("relate_prepare", arguments=[
                    "relate_prepare",
                    "--catalogue={{ params.catalog }}",
                    "--collection={{ params.collection }}",
                    "--attribute={{ params.relation }}",
                    "--mode=full"
                ])

                process = UploadOperator("relate_process", arguments=[
                    "--message-data",
                    "{{ json.dumps(task_instance.xcom_pull('relate_prepare')) }}",
                    "relate_process"
                ])

                update = UploadOperator("import_upload", arguments=[
                    "--message-data",
                    "{{ json.dumps(task_instance.xcom_pull('relate_process')) }}",
                    "full_update"
                ])

                apply = UploadOperator("apply_events", arguments=[
                    "--message-data",
                    "{{ json.dumps(task_instance.xcom_pull('import_upload')) }}",
                    "apply"
                ])

                update_view = UploadOperator("update_view", arguments=[
                    "--message-data",
                    "{{ json.dumps(task_instance.xcom_pull('apply_events')) }}",
                    "relate_update_view"
                ])

                check = UploadOperator("check", arguments=[
                    "--message-data",
                    "{{ json.dumps(task_instance.xcom_pull('update_view')) }}",
                    "relate_check"
                ])

            prepare >> process >> update >> apply >> update_view >> check
