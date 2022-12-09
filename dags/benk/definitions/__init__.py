import importlib
from pathlib import Path
from typing import Iterator, Union, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from benk.workflow import Relate, Import


Handler = Union["Relate", "Import"]


class RelateArguments(BaseModel):
    attribute: str = ...
    mode: str = "update"


class ImportArguments(BaseModel):
    application: str = ...
    mode: str = "full"


class Workflow(BaseModel):
    workflow: str
    arguments: Union[ImportArguments, RelateArguments]

    @property
    def handler(self) -> Handler:
        class_name = self.workflow.title()
        module = importlib.import_module("benk.workflow", class_name)
        return getattr(module, class_name)


class Collection(BaseModel):
    collection: str
    workflows: list[Workflow]


class Model(BaseModel):
    catalog: str
    collections: list[Collection]


class _Definitions:

    # were in /opt/airflow
    _path = Path.cwd() / "dags" / "benk" / "definitions"

    def __iter__(self) -> Iterator[Model]:
        for obj in self._path.glob("*.json"):
            yield Model.parse_file(obj, encoding="utf-8")


DEFINITIONS = _Definitions()
