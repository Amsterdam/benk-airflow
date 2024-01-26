import json
from unittest.mock import patch, call

from freezegun import freeze_time

from benk.common import BaseOperaterArgs, START_DATE, MAX_ACTIVE_TASKS


class MockDag:
    type = ""

    def __init__(self, *args):
        self.id = f"{self.type}-{'_'.join(args)}"

    def get_leaf_nodes(self):
        return [self.id]

    def get_start_nodes(self):
        return [self.id]


class MockImportDag(MockDag):
    type = "import"


class MockRelateDag(MockDag):
    type = "relate"


class MockPrepareDag(MockDag):
    type = "prepare"


class MockInitialiseDag(MockDag):
    type = "initialise"


class TestGenerate:

    @freeze_time("2022-12-05")
    def test_generate(self, model_definition):
        with (
            patch("airflow.DAG") as mock_dag,
            patch("benk.workflow.Import", MockImportDag),
            patch("benk.workflow.Relate", MockRelateDag),
            patch("benk.workflow.Prepare", MockPrepareDag),
            patch("benk.workflow.Initialise", MockInitialiseDag),
            patch("airflow.models.baseoperator.cross_downstream") as mock_cross_downstream,
            patch("airflow.models.param.Param") as mock_param
        ):

            # run generate DAG
            import benk.generate

            mock_dag.assert_called_with(
                dag_id="nap",
                tags=["nap"],
                default_args=BaseOperaterArgs,
                template_searchpath=["/"],
                user_defined_macros={"json": json},
                schedule_interval=None,
                catchup=False,
                start_date=START_DATE,
                max_active_tasks=MAX_ACTIVE_TASKS,
                params={'relate_mode': mock_param.return_value},
                schedule="my schedule"
            )

            mock_param.assert_called_with(type="string", default="update")

            mock_cross_downstream.assert_has_calls([
                call(["initialise-"], ["import-nap_peilmerken_Grondslag"]),
                call(["import-nap_peilmerken_Grondslag"],
                     ["relate-nap_peilmerken_relation_attribute_1", "relate-nap_peilmerken_relation_attribute_2"]),
                call(["prepare-nap"], ["initialise-"])
            ])
