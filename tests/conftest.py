from pathlib import Path

import pytest

from benk.definitions import DEFINITIONS, _Definitions


@pytest.fixture
def model_definition(monkeypatch):
    with monkeypatch.context():
        monkeypatch.setattr(
            "benk.definitions.DEFINITIONS",
            _Definitions(Path(__file__).parent / "fixtures" / "definitions")
        )
        return list(DEFINITIONS)
