import json

from airflow import DAG
from airflow.models.baseoperator import cross_downstream

from benk.common import START_DATE, BaseOperaterArgs
from benk.definitions import DEFINITIONS
from benk.utils import flatten_list
from benk.workflow import Import, Initialise, Prepare, Relate

for definition in DEFINITIONS:
    name = definition.dag_id
    kwargs = dict(definition.dagParameters or {})

    with DAG(
        dag_id=name,
        tags=[name],
        default_args=BaseOperaterArgs,
        template_searchpath=["/"],
        user_defined_macros={"json": json},
        schedule_interval=None,
        catchup=False,
        start_date=START_DATE,  # fix start date
        max_active_tasks=MAX_ACTIVE_TASKS,
        **kwargs
    ):
        initialise = Initialise()

        imports = []
        relates = []
        for collection in definition.collections:
            imports.append(Import(definition.catalog, collection.collection, collection.import_.application))

            relates += [
                Relate(definition.catalog, collection.collection, relation) for relation in collection.relations
            ]

        # Start with initialising / migrating before imports
        cross_downstream(initialise.get_leaf_nodes(), flatten_list([i.get_start_nodes() for i in imports]))

        # Link imports to relates
        cross_downstream(
            flatten_list([i.get_leaf_nodes() for i in imports]), flatten_list([r.get_start_nodes() for r in relates])
        )

        if definition.prepare:
            prepare = Prepare(definition.catalog)

            # Add Prepare
            cross_downstream(prepare.get_leaf_nodes(), initialise.get_start_nodes())
