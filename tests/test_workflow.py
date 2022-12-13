import pytest
from benk.workflow import Import, Relate


class TestWorkflow:

    def test_import(self):
        import_ = Import()
        tasks = import_.tasks()
        assert len(tasks) == 5

        names = ["import", "update", "compare", "upload", "apply"]
        assert all(task.name == name for task, name in zip(tasks, names))

    def test_relate(self):
        relate = Relate()
        tasks = relate.tasks()
        assert len(tasks) == 6

        # Notice: dash instead of underscore for update_view
        names = ["prepare", "process", "update", "apply", "update-view", "check"]
        assert all(task.name == name for task, name in zip(tasks, names))
