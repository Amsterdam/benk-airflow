from airflow.exceptions import AirflowSkipException
from airflow.models.baseoperator import BaseOperator, chain
from airflow.operators.python import PythonOperator

from benk.workflow.workflow import BaseDAG, ImportArgs, UploadArgs, XCom


class Import(BaseDAG):
    """Holds the tasks to build an Import DAG."""

    XCOM_MAPPER = {"compare": "import", "upload": "compare", "apply": "upload"}

    def __init__(self, catalogue: str, collection: str, application: str):
        self.catalogue = catalogue
        self.collection = collection
        self.application = application

        self._tasks: list[BaseOperator] = []
        self._init()

    @property
    def id(self) -> str:
        """Return Id of import DAG."""
        return f"import_{self.catalogue}_{self.collection}_{self.application}"

    def _import(self):
        name = "import"
        return self.Operator(
            name=name,  # = podname + random suffix
            task_id=self.get_taskid(name),
            arguments=[
                "import",
                f"--catalogue={self.catalogue}",
                f"--collection={self.collection}",
                f"--application={self.application}",
                "--mode={{ params.import_mode }}",
            ],
            **ImportArgs,
        )

    def _update(self):
        name = "update"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=[
                "apply",
                f"--catalogue={self.catalogue}",
                f"--collection={self.collection}",
            ],
            **UploadArgs,
        )

    def _compare(self):
        name = "compare"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["--message-data", XCom.get_template(), "compare"],
            params=XCom.get_param(self.get_taskid(self.XCOM_MAPPER[name])),
            **UploadArgs,
        )

    def _upload(self):
        name = "upload"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["--message-data", XCom.get_template(), "full_update"],
            params=XCom.get_param(self.get_taskid(self.XCOM_MAPPER[name])),
            **UploadArgs,
        )

    def _apply(self):
        name = "apply"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["--message-data", XCom.get_template(), "apply"],
            params=XCom.get_param(self.get_taskid(self.XCOM_MAPPER[name])),
            **UploadArgs,
        )

    def _init(self):
        self._tasks = [self._import(), self._update(), self._compare(), self._upload(), self._apply()]
        chain(*self._tasks)

    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the last nodes in this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[-1]]

    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[0]]


def _skip_operator():
    raise AirflowSkipException("Import skipped")


class ImportSkipped(Import):
    """Class representing tasks container that will be skipped when run."""

    def _import(self):
        name = "import"
        return PythonOperator(task_id=self.get_taskid(name), python_callable=_skip_operator)

    def _update(self):
        name = "update"
        return PythonOperator(task_id=self.get_taskid(name), python_callable=_skip_operator)

    def _compare(self):
        name = "compare"
        return PythonOperator(task_id=self.get_taskid(name), python_callable=_skip_operator)

    def _upload(self):
        name = "upload"
        return PythonOperator(task_id=self.get_taskid(name), python_callable=_skip_operator)

    def _apply(self):
        name = "apply"
        return PythonOperator(task_id=self.get_taskid(name), python_callable=_skip_operator)
