import importlib
from typing import TYPE_CHECKING, Iterator, Union

from benk.common import AIRFLOW_HOME
from pydantic import BaseModel

if TYPE_CHECKING:
    from benk.workflow import Import, Relate


Handler = Union["Relate", "Import"]


class RelateArguments(BaseModel):
    """Argument definition for Relate workflow."""

    attribute: str
    mode: str = "update"


class ImportArguments(BaseModel):
    """Argument definition for Import workflow."""

    application: str
    mode: str = "full"


class Workflow(BaseModel):
    """Workflow definition(s). Requires a handler in benk.workflow."""

    workflow: str
    arguments: Union[ImportArguments, RelateArguments]

    @property
    def handler(self) -> Handler:
        """Returns handler belonging to `workflow`."""
        class_name = self.workflow.title()

        try:
            module = importlib.import_module("benk.workflow", class_name)
        except ImportError:
            raise ImportError(f"Workflow handler not found: {class_name}")

        return getattr(module, class_name)


class Collection(BaseModel):
    """
    Collection definition.

    Example:
        "collection": "peilmerken",
        "workflows": [{"workflow": "workflow", "arguments": {}]
    """

    collection: str
    workflows: list[Workflow]


class Model(BaseModel):
    """Root model definition, should contain 1 catalog and 1 or more collections."""

    catalog: str
    collections: list[Collection]


class _Definitions:

    _path = AIRFLOW_HOME / "dags" / "benk" / "definitions"

    def __iter__(self) -> Iterator[Model]:
        """Yields a parsed Model from all json objects found in path."""
        for obj in self._path.glob("*.json"):
            yield Model.parse_file(obj, encoding="utf-8")


DEFINITIONS = _Definitions()
