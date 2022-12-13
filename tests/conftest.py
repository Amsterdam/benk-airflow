from pathlib import Path

import pytest
from benk.definitions import DEFINITIONS


@pytest.fixture
def model_definition(monkeypatch):
    with monkeypatch.context():
        monkeypatch.setattr(
            "benk.definitions._Definitions._path",
            Path(__file__).parent / "fixtures"
        )
        return list(DEFINITIONS)
