from benk.environment import GrondslagEnvironment


class TestEnvironment:

    def test_env_vars(self):
        settings = GrondslagEnvironment()
        keys = [val.name for val in settings.env_vars()]
        assert "env_vars" not in keys
        assert "GRONDSLAG_DATABASE_PASSWORD" in keys
        assert "GRONDSLAG_DATABASE_PORT" in keys
