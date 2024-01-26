from airflow.models.baseoperator import BaseOperator, chain
from airflow.utils.trigger_rule import TriggerRule

from benk.workflow.workflow import BaseDAG, UploadArgs, XCom


class Relate(BaseDAG):
    """Holds the tasks to build a Relate DAG."""

    XCOM_MAPPER = {
        "process": "prepare",
        "upload": "process",
        "apply": "upload",
        "update_view": "apply",
        "check": "update_view",
    }

    def __init__(self, catalogue: str, collection: str, attribute: str):
        self.catalogue = catalogue
        self.collection = collection
        self.attribute = attribute

        self._tasks: list[BaseOperator] = []
        self._init()

    @property
    def id(self) -> str:
        """Return Id of the relate DAG."""
        return f"relate_{self.catalogue}_{self.collection}_{self.attribute}"

    def _prepare(self):
        name = "prepare"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=[
                "relate_prepare",
                f"--catalogue={self.catalogue}",
                f"--collection={self.collection}",
                f"--attribute={self.attribute}",
                "--mode={{ params.relate_mode }}",
            ],
            trigger_rule=TriggerRule.ALL_DONE,  # trigger task when dependency is done, fail or success
            **UploadArgs,
        )

    def _process(self):
        name = "process"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["--message-data", XCom.get_template(), "relate_process"],
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

    def _update_view(self):
        name = "update_view"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["--message-data", XCom.get_template(), "relate_update_view"],
            params=XCom.get_param(self.get_taskid(self.XCOM_MAPPER[name])),
            **UploadArgs,
        )

    def _check(self):
        name = "check"
        return self.Operator(
            name=name,
            task_id=self.get_taskid(name),
            arguments=["--message-data", XCom.get_template(), "relate_check"],
            params=XCom.get_param(self.get_taskid(self.XCOM_MAPPER[name])),
            **UploadArgs,
        )

    def _init(self):
        self._tasks = [
            self._prepare(),
            self._process(),
            self._upload(),
            self._apply(),
            self._update_view(),
            self._check(),
        ]
        chain(*self._tasks)

    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the last nodes in this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[-1]]

    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        return [self._tasks[0]]
