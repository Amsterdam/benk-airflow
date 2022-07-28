from benk.environment import GrondslagEnvironment
import pytest
from airflow.models import Variable


class TestEnvironment:

    @pytest.fixture
    def initialise_empty_env(self):
        """Initialise settings which have no default value set."""
        Variable.set("GRONDSLAG_DATABASE_PASSWORD", "secret_password")

    def test_env_vars(self, initialise_empty_env):
        settings = GrondslagEnvironment()
        keys = [val.name for val in settings.env_vars()]
        assert "env_vars" not in keys
        assert "GRONDSLAG_DATABASE_PASSWORD" in keys
        assert "GRONDSLAG_DATABASE_PORT" in keys
