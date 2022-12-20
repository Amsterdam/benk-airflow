from airflow.models.baseoperator import BaseOperator, chain

from benk.workflow.workflow import BaseDAG, ImportArgs, UploadArgs


class Import(BaseDAG):
    """Holds the tasks to build an Import DAG."""

    def __init__(self, catalogue: str, collection: str, application: str):
        self.catalogue = catalogue
        self.collection = collection
        self.application = application

        self.id = f"import_{catalogue}_{collection}_{application}"
        self._tasks: list[BaseOperator] = []
        self._init()

    def _import(self):
        return self.Operator(
            task_id=f"{self.id}-import",
            name="import",  # required
            arguments=[
                "import",
                f"--catalogue={self.catalogue}",
                f"--collection={self.collection}",
                f"--application={self.application}",
            ],
            **ImportArgs,
        )

    def _update(self):
        return self.Operator(
            task_id=f"{self.id}-update",
            name="update",
            arguments=[
                "apply",
                f"--catalogue={self.catalogue}",
                f"--collection={self.collection}",
            ],
            **UploadArgs,
        )

    def _compare(self):
        return self.Operator(
            task_id=f"{self.id}-compare",
            name="compare",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('import')) }}",
                "compare",
            ],
            **UploadArgs,
        )

    def _upload(self):
        return self.Operator(
            task_id=f"{self.id}-upload",
            name="upload",
            arguments=[
                "--message-data",
                "{{ json.dumps(task_instance.xcom_pull('compare')) }}",
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
                "{{ json.dumps(task_instance.xcom_pull('upload')) }}",
                "apply",
            ],
            **UploadArgs,
        )

    def _init(self):
        self._tasks = [
            self._import(),
            self._update(),
            self._compare(),
            self._upload(),
            self._apply()
        ]
        chain(*self._tasks)

    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the last nodes in this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[-1]]

    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[0]]
