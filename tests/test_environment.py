from unittest import mock

from tests.mocks import mock_get_variable


@mock.patch("airflow.models.Variable", mock_get_variable)
class TestEnvironment:

    def test_env_vars(self):
        from benk.environment import GrondslagEnvironment
        settings = GrondslagEnvironment()
        keys = [val.name for val in settings.env_vars()]
        assert "env_vars" not in keys
        assert "GRONDSLAG_DATABASE_PASSWORD" in keys
        assert "GRONDSLAG_DATABASE_PORT" in keys

    def test_prepare_env(self):
        from benk.environment import PrepareServiceEnvironment

        assert hasattr(PrepareServiceEnvironment, "GOB_PREPARE_DATABASE_HOST")
        assert hasattr(PrepareServiceEnvironment, "NRBIN_DATABASE_HOST")
        assert hasattr(PrepareServiceEnvironment, "BASISINFORMATIE_OBJECTSTORE_TENANT_ID")
