from airflow.models.baseoperator import BaseOperator, chain

from benk.workflow.workflow import BaseDAG, UploadArgs


class Relate(BaseDAG):
    """Holds the tasks to build a Relate DAG."""

    def __init__(self, catalogue: str, collection: str, attribute: str):
        self.catalogue = catalogue
        self.collection = collection
        self.attribute = attribute

        self.id = f"relate_{catalogue}_{collection}_{attribute}"
        self._tasks: list[BaseOperator] = []
        self._init()

    def _prepare(self):
        return self.Operator(
            task_id=f"{self.id}-prepare",
            name="prepare",
            arguments=[
                "relate_prepare",
                f"--catalogue={self.catalogue}",
                f"--collection={self.collection}",
                f"--attribute={self.attribute}",
            ],
            **UploadArgs,
        )

    def _process(self):
        return self.Operator(
            task_id=f"{self.id}-process",
            name="process",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('prepare')) }}",
                "relate_process",
            ],
            **UploadArgs,
        )

    def _update(self):
        return self.Operator(
            task_id=f"{self.id}-update",
            name="update",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('process')) }}",
                "full_update",
            ],
            **UploadArgs,
        )

    def _apply(self):
        return self.Operator(
            task_id=f"{self.id}-apply",
            name="apply",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('update')) }}",
                "apply",
            ],
            **UploadArgs,
        )

    def _update_view(self):
        return self.Operator(
            task_id=f"{self.id}-update_view",
            name="update_view",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('apply')) }}",
                "relate_update_view",
            ],
            **UploadArgs,
        )

    def _check(self):
        return self.Operator(
            task_id=f"{self.id}-check",
            name="check",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('update_view')) }}",
                "relate_check",
            ],
            **UploadArgs,
        )

    def _init(self):
        self._tasks = [
            self._prepare(),
            self._process(),
            self._update(),
            self._apply(),
            self._update_view(),
            self._check()
        ]
        chain(*self._tasks)

    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the last nodes in this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[-1]]

    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[0]]
