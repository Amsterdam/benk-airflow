import json
from pathlib import Path

from airflow.models import BaseOperator
from benk.utils import flatten_list
from benk.workflow.workflow import BaseDAG, PrepareArgs


class _PrepareDefinition:
    CONFIG_DIR = Path(__file__).parent / '..' / 'prepare_config'

    def __init__(self, catalogue: str):
        self.catalogue = catalogue

    def get(self):
        """Fetch the last version of the prepare definition from GitHub."""
        with open(self.CONFIG_DIR / f'{self.catalogue}.prepare.json') as f:
            return json.load(f)


class Prepare(BaseDAG):
    """Holds the logic to build the DAG for a given prepare job, based on its prepare configuration."""

    def __init__(self, catalogue: str):
        self.catalogue = catalogue

        self._tasks: list[BaseOperator] = []
        self._leaf_nodes: list[BaseOperator] = []
        self._start_nodes: list[BaseOperator] = []

        self._init()

    @property
    def id(self) -> str:
        return f"prepare_{self.catalogue}"

    def _prepare_task_operator(self, action_id: str):
        return self.Operator(
            task_id=f"{self.id}-prepare-{action_id}",
            name=f"{self.catalogue}_task_{action_id}",
            arguments=[
                "prepare_task",
                f"--catalogue={self.catalogue}",
                f"--task_name={action_id}"
            ],
            **PrepareArgs,
        )

    def _init(self):
        config = _PrepareDefinition(self.catalogue).get()
        actions = config['actions']

        tasks = {action['id']: self._prepare_task_operator(action['id']) for action in actions}

        # Collect actions that depend on all other actions (depends_on == '*')
        final_action_ids = [action['id'] for action in actions if action.get('depends_on') == '*']

        # Determine leaf_nodes
        all_dependencies = flatten_list(
            [action.get('depends_on', []) for action in actions if action.get('depends_on') != '*'])
        leaf_nodes = [task for task_id, task in tasks.items() if
                      task_id not in all_dependencies and task_id not in final_action_ids]

        # Set dependencies for all actions
        for action in actions:
            task = tasks[action['id']]

            if action.get('depends_on') == '*':
                task << leaf_nodes
            elif depends_on := action.get('depends_on', []):
                depends_on_tasks = [tasks[depends_on_id] for depends_on_id in depends_on]
                task << depends_on_tasks

        self._tasks = list(tasks.values())

        self._leaf_nodes = leaf_nodes if not final_action_ids else [
            tasks[action_id] for action_id in final_action_ids
        ]

        start_actions = [action for action in actions if not action.get('depends_on')]
        self._start_nodes = [tasks[action['id']] for action in start_actions]

    def get_leaf_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        return self._leaf_nodes

    def get_start_nodes(self) -> list[BaseOperator]:
        """Return the start nodes of this DAG. Used to link this DAG to other DAGs."""
        return self._start_nodes
