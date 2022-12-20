from unittest import TestCase
from unittest.mock import patch

from tests.mocks import mock_get_variable, mock_prepare_configs_dir


class MockOperator:
    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id
        self.depends_on = []

    def __lshift__(self, other):
        self.depends_on = [o.task_id for o in other]


@patch("airflow.models.Variable", mock_get_variable)
class TestPrepare(TestCase):

    def test_prepare(self):
        from benk.workflow import Prepare
        Prepare.Operator = MockOperator

        with patch("benk.workflow.prepare._PrepareDefinition.CONFIG_DIR", mock_prepare_configs_dir):
            prepare_dag = Prepare("test_config")

            self.assertEqual(["prepare_test_config-prepare-action6"], [t.task_id for t in prepare_dag.get_leaf_nodes()])
            self.assertEqual(["prepare_test_config-prepare-action1", "prepare_test_config-prepare-action1b"],
                             [t.task_id for t in prepare_dag.get_start_nodes()])

            expected_dependencies = {
                "prepare_test_config-prepare-action1": [],
                "prepare_test_config-prepare-action1b": [],
                "prepare_test_config-prepare-action2": ["prepare_test_config-prepare-action1"],
                "prepare_test_config-prepare-action3": ["prepare_test_config-prepare-action1",
                                                        "prepare_test_config-prepare-action2",
                                                        "prepare_test_config-prepare-action1b"],
                "prepare_test_config-prepare-action4": ["prepare_test_config-prepare-action2",
                                                        "prepare_test_config-prepare-action3"],
                "prepare_test_config-prepare-action5": ["prepare_test_config-prepare-action3"],

                # Important one, this is auto-generated based on 4 and 5 being leaves without the "*" dependency of
                # prepare_test_config-prepare-action6
                "prepare_test_config-prepare-action6": ["prepare_test_config-prepare-action4",
                                                        "prepare_test_config-prepare-action5"],
            }

            # Assert all expected tasks are present
            self.assertEqual(len(prepare_dag._tasks), 7)
            self.assertEqual(set([t.task_id for t in prepare_dag._tasks]), set(expected_dependencies.keys()))

            # Assert that dependencies are set correctly
            for task in prepare_dag._tasks:
                self.assertEqual(task.depends_on, expected_dependencies[task.task_id])
