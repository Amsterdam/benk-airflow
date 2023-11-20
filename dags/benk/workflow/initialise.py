from airflow.models.baseoperator import BaseOperator, chain
from benk.workflow.workflow import BaseDAG, UploadArgs


class Initialise(BaseDAG):
    """DAG containing initial tasks to perform before starting jobs."""

    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return leaf node(s). In this case should be 1 node."""
        return [self._tasks[-1]]

    def get_start_nodes(self) -> list[BaseOperator]:
        """Return start node(s). In this case should be 1 node."""
        return [self._tasks[0]]

    @property
    def id(self) -> str:
        """Name to identify this DAG."""
        return "initialise"

    def __init__(self):
        self._tasks = [self._migrate()]
        chain(*self._tasks)

    def _migrate(self):
        name = "migrate"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["migrate"],
            **UploadArgs,
        )
