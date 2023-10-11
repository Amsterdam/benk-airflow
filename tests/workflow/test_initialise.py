from unittest import mock, TestCase


class TestWorkflow(TestCase):

    @mock.patch("benk.workflow.import_.chain")
    def setUp(self, mock_chain):
        from benk.workflow import Initialise
        self.mock_chain = mock_chain
        self.init = Initialise()

    def test_initialise(self):
        init_ = self.init
        assert init_.id == "initialise"
        assert len(init_._tasks) == 1

        names = ["migrate"]
        assert all(task.name == name for task, name in zip(init_._tasks, names))

        leafs = ["migrate"]
        starts = ["migrate"]

        assert [n.name for n in init_.get_leaf_nodes()] == leafs
        assert [n.name for n in init_.get_start_nodes()] == starts
