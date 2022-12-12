from pathlib import Path

import pytest
# from airflow.models import Variable
from benk.definitions import DEFINITIONS

# def pytest_generate_tests(metafunc):
#     """Set required variables to fake values."""
#     variables = {
#         "GRONDSLAG_DATABASE_PASSWORD": "secret_password",
#         "GRONDSLAG_DATABASE_HOST": "DBXYZ.AMSTERDAM.NL",
#         "GRONDSLAG_DATABASE": "peilmerken",
#         "GRONDSLAG_DATABASE_USER": "userX"
#     }
#     for k, v in variables:
#         Variable.set(k, v)
#
#     yield
#
#     for k, v in variables:
#         Variable.delete(k, v)
#
#
# def airflow_environment():
#     with mock.patch.dict("os.environ", AIRFLOW_VAR_KEY="env-value"):
#         assert "env-value" == Variable.get("key")


@pytest.fixture
def model_definition(monkeypatch):
    with monkeypatch.context():
        monkeypatch.setattr(
            "benk.definitions._Definitions._path",
            Path(__file__).parent / "fixtures"
        )
        return list(DEFINITIONS)
