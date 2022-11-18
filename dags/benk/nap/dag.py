"""Dag which imports NAP.

Order of tasks is as it was defined in gob. See gobworkflow/workflow/config.py.
"""
import json
from datetime import datetime

from airflow import DAG

from benk.common import TEAM_NAME, BaseOperaterArgs
from benk.environment import GrondslagEnvironment, GOBEnvironment, GenericEnvironment
from benk.workflow import Import

env_vars = GenericEnvironment().env_vars() + GOBEnvironment().env_vars() + GrondslagEnvironment().env_vars()

dag_default_args = {
    "default_args": BaseOperaterArgs | {"env_vars": env_vars},  # operater kwargs
    "schedule_interval": None,
    "catchup": False,
    "start_date": datetime.utcnow(),
    "user_defined_macros": {"json": json},  # must be in the same module as DAG
    "template_searchpath": ["/"]
}

params = {
    "catalogue": "nap",
    "collection": "peilmerken",
    "application": "Grondslag",
    "mode": "full"
}

with DAG(
    dag_id=f"{TEAM_NAME}_{'_'.join(params.values())}",
    params=params,
    tags=["import", "update", "compare", "store", "apply"],
    **dag_default_args
):
    Import.workflow()
