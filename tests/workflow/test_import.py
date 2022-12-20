from unittest import mock

from tests.mocks import mock_get_variable


@mock.patch("airflow.models.Variable", mock_get_variable)
class TestWorkflow:

    def test_import(self):
        from benk.workflow import Import
        with mock.patch("benk.workflow.import_.chain") as mock_chain:
            import_ = Import("catalog", "collection", "application")
            assert len(import_._tasks) == 5

            names = ["import", "update", "compare", "upload", "apply"]
            assert all(task.name == name for task, name in zip(import_._tasks, names))


            leafs = ["apply"]
            starts = ["import"]

            assert [n.name for n in import_.get_leaf_nodes()] == leafs
            assert [n.name for n in import_.get_start_nodes()] == starts

            mock_chain.assert_called_with(*import_._tasks)
