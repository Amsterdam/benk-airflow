from unittest.mock import patch, mock_open
from pathlib import Path

from tests.mocks import mock_definitions


class TestUpdate:

    @patch("benk.prepare_config.update.DEFINITIONS", mock_definitions)
    @patch("benk.prepare_config.update.shutil")
    def test_update(self, mock_shutil):
        from benk.prepare_config.update import update

        update()

        dags_path = Path(__file__).parent.parent.parent / 'dags'
        mock_shutil.copyfile.assert_called_with(
            dags_path / 'GOB-Prepare' / 'src' / 'data' / 'nap.prepare.json',
            dags_path / 'benk' / 'prepare_config' / 'nap.prepare.json',
        )