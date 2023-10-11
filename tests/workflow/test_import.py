from unittest import mock, TestCase


class TestWorkflow(TestCase):

    @mock.patch("benk.workflow.import_.chain")
    def setUp(self, mock_chain):
        from benk.workflow import Import
        self.mock_chain = mock_chain
        self.import_ = Import("cat", "col", "app")

    def test_import(self):
        import_ = self.import_

        assert import_.id == "import_cat_col_app"
        assert len(import_._tasks) == 5

        names = ["import", "update", "compare", "upload", "apply"]
        assert all(task.name == name for task, name in zip(import_._tasks, names))

        leafs = ["apply"]
        starts = ["import"]

        assert [n.name for n in import_.get_leaf_nodes()] == leafs
        assert [n.name for n in import_.get_start_nodes()] == starts

        self.mock_chain.assert_called_with(*import_._tasks)

    def test_get_taskid(self):
        ids = [
            "import_cat_col_app-import",
            "import_cat_col_app-update",
            "import_cat_col_app-compare",
            "import_cat_col_app-upload",
            "import_cat_col_app-apply"
        ]
        assert all(task.task_id == id_ for task, id_ in zip(self.import_._tasks, ids))

    def test_xcom_param(self):
        from benk.workflow.workflow import XCom
        mapper = self.import_.XCOM_MAPPER

        for task in self.import_._tasks:
            if task.name in mapper:
                assert task.params["xcom_task_id"] == self.import_.get_taskid(mapper[task.name])
                assert XCom.get_template() in task.arguments
            else:
                assert "xcom_task_id" not in task.params
                assert XCom.get_template() not in task.arguments
