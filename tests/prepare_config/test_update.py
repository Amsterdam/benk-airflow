from unittest.mock import patch, mock_open
from pathlib import Path

from tests.mocks import mock_definitions


class TestUpdate:

    @patch("benk.prepare_config.update.GITHUB_BASE_URL", "http://github")
    @patch("benk.prepare_config.update.DEFINITIONS", mock_definitions)
    @patch("benk.prepare_config.update.requests")
    def test_update(self, mock_requests):
        from benk.prepare_config.update import update

        m = mock_open()
        with patch("builtins.open", m):
            mock_requests.get.return_value.text = "File contents"

            update()

        benk_path = Path(__file__).parent.parent.parent / 'dags' / 'benk'
        m.assert_called_once_with(benk_path / 'prepare_config' / "nap.prepare.json", "w")
        handle = m()
        handle.write.assert_called_once_with("File contents")

        mock_requests.get.assert_called_with("http://github/src/data/nap.prepare.json")