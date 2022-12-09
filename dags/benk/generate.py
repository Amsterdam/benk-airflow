import json
from datetime import datetime

from airflow.models.dag import DAG

from benk.common import BaseOperaterArgs
from benk.definitions import DEFINITIONS


dag_default_args = {
    "default_args": BaseOperaterArgs,
    "template_searchpath": ["/"],
    "user_defined_macros": {"json": json},
    "schedule_interval": None,
    "catchup": False,
    "start_date": datetime.utcnow()
}


for definition in DEFINITIONS:
    for collection in definition.collections:
        for workflow in collection.workflows:
            name = workflow.workflow
            print(f"Loading: {definition.catalog.upper()} - {collection.collection} - {name}")

            params = {
                "catalogue": definition.catalog,
                "collection": collection.collection,
                **workflow.arguments.dict()
            }

            with DAG(
                dag_id="_".join(params.values()),
                params=params,
                tags=[name, *params.values()],
                **dag_default_args
            ):
                workflow.handler.create_dag()
