import json
from datetime import datetime
from unittest.mock import patch, call

from freezegun import freeze_time

from benk.common import BaseOperaterArgs
from tests.mocks import mock_get_variable


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


@patch("airflow.models.Variable", mock_get_variable)
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
            patch("airflow.models.baseoperator.chain") as mock_chain
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
                start_date=datetime.utcnow(),
            )

            mock_chain.assert_has_calls([
                call('initialise-', ['import-nap_peilmerken_Grondslag']),
                call(['prepare-nap'], 'initialise-')
            ])

            mock_cross_downstream.assert_has_calls([
                call(["import-nap_peilmerken_Grondslag"],
                     ["relate-nap_peilmerken_relation_attribute_1", "relate-nap_peilmerken_relation_attribute_2"]),
            ])
