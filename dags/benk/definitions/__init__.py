from pathlib import Path
from typing import Iterator, Optional

from pydantic import BaseModel, Field


class _DagParameters(BaseModel):
    """Extra parameters passed to the DAG."""

    schedule: Optional[str] = None


class _Import(BaseModel):
    application: str


class _Collection(BaseModel):
    """
    Collection definition.

    Example:
        "collection": "peilmerken",
        "workflows": [{"workflow": "workflow", "arguments": {}]
    """

    collection: str
    import_: _Import = Field(alias="import")
    relations: list[str]


class _Model(BaseModel):
    """Root model definition, should contain 1 catalog and 1 or more collections."""

    catalog: str
    dagParameters: Optional[_DagParameters]
    prepare: Optional[bool] = False
    collections: list[_Collection]


class _Definitions:
    def __init__(self, path: Path):
        self._path = path

    def __iter__(self) -> Iterator[_Model]:
        """Yield a parsed Model from all json objects found in path."""
        objs = list(self._path.glob("*.json"))

        if not objs:
            raise FileNotFoundError(f"Definitions folder is empty: {self._path}")

        for obj in sorted(objs):
            yield _Model.parse_file(obj, encoding="utf-8")


DEFINITIONS = _Definitions(Path(__file__).parent)
