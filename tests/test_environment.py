import unittest
from unittest.mock import patch, call


class TestEnvironment(unittest.TestCase):

    @patch("benk.environment.mask_secret")
    def test_env_vars(self, mock_mask):
        from benk.environment import GrondslagEnvironment
        settings = GrondslagEnvironment()
        keys = [val.name for val in settings.env_vars()]

        mock_mask.assert_has_calls([
            call({'GRONDSLAG_DATABASE': "{{ var.value.get('grondslag-db') }}"}),
            call({'GRONDSLAG_DATABASE_HOST': "{{ var.value.get('grondslag-host') }}"}),
            call({'GRONDSLAG_DATABASE_PASSWORD': "{{ var.value.get('grondslag-password') }}"}),
            call({'GRONDSLAG_DATABASE_PORT': "{{ var.value.get('grondslag-port') }}"}),
            call({'GRONDSLAG_DATABASE_USER': "{{ var.value.get('grondslag-user') }}"})
        ])
        assert "env_vars" not in keys
        assert "GRONDSLAG_DATABASE_PASSWORD" in keys
        assert "GRONDSLAG_DATABASE_PORT" in keys

    def test_prepare_env(self):
        from benk.environment import PrepareServiceEnvironment

        assert hasattr(PrepareServiceEnvironment, "GOB_PREPARE_DATABASE_HOST")
        assert hasattr(PrepareServiceEnvironment, "NRBIN_DATABASE_HOST")
        assert hasattr(PrepareServiceEnvironment, "BASISINFORMATIE_OBJECTSTORE_TENANT_ID")
