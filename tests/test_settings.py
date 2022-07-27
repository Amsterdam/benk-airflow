from benk.settings import Settings
import pytest
from airflow.models import Variable


class TestSettings:

    @pytest.fixture
    def initialise_empty_settings(self):
        """Initialise settings which have no default value set."""
        Variable.set("GRONDSLAG_DATABASE_PASSWORD", "secret_password")

    def test_settings_env_vars(self, initialise_empty_settings):
        settings = Settings()
        keys = [val.name for val in settings.env_vars()]
        assert "env_vars" not in keys
        assert "GRONDSLAG_DATABASE_PASSWORD" in keys
        assert "GRONDSLAG_DATABASE_PORT" in keys
