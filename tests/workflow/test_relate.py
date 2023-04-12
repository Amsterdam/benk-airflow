from unittest import mock, TestCase

from airflow.utils.trigger_rule import TriggerRule
from tests.mocks import mock_get_variable


@mock.patch("airflow.models.Variable", mock_get_variable)
class TestWorkflow(TestCase):

    def test_relate(self):
        from benk.workflow import Relate
        with mock.patch("benk.workflow.relate.chain") as mock_chain:
            relate = Relate('catalogue', 'collection', 'attribute')
            assert len(relate._tasks) == 6

            # Notice: dash instead of underscore for update_view
            names = ["prepare", "process", "update", "apply", "update-view", "check"]
            assert all(task.name == name for task, name in zip(relate._tasks, names))

            leafs = ["check"]
            starts = ["prepare"]

            assert [n.name for n in relate.get_leaf_nodes()] == leafs
            assert [n.name for n in relate.get_start_nodes()] == starts

            mock_chain.assert_called_with(*relate._tasks)

            assert relate.get_start_nodes()[0].trigger_rule == TriggerRule.ALL_DONE

