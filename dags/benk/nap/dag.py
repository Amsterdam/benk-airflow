"""Dag which imports NAP.

Order of tasks is as it was defined in gob. See gobworkflow/workflow/config.py.
"""
from datetime import datetime

from airflow import DAG

from benk.common import default_args, TEAM_NAME
from benk.tasks import ImportOperator, UploadOperator

dag_default_args = {
    "default_args": default_args,
    "schedule_interval": None,
    "catchup": False,
    "start_date": datetime.utcnow()
}

params = {
    "catalogue": "nap",
    "collection": "peilmerken",
    "mode": "full"
}


with DAG(
    dag_id=f"{TEAM_NAME}_{'_'.join(params.values())}",
    params=params,
    tags=["import", "update", "compare", "store", "apply"],
    **dag_default_args
):
    nap_import = ImportOperator("nap_import", arguments=[
            "import",
            "--catalogue={{ params.catalog }}",
            "--collection={{ params.collection }}",
            "--mode={{ params.mode }}"
        ]
    )

    update_model = UploadOperator("update_model", arguments=[
            "apply",
            "--catalogue=nap",
            "--collection=peilmerken"
        ]
    )

    import_compare = UploadOperator("import_compare", arguments=[
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('nap_import')) }}",
            "compare"
        ]
    )

    import_upload = UploadOperator("import_upload", arguments=[
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('import_compare')) }}",
            "full_update"
        ]
    )

    apply_events = UploadOperator("apply_events", arguments=[
            "--message-data",
            "{{ json.dumps(task_instance.xcom_pull('import_upload')) }}",
            "apply"
        ]
    )

nap_import >> update_model >> import_compare >> import_upload >> apply_events
