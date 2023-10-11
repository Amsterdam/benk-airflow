from pathlib import Path

from benk.definitions import _Definitions

mock_definitions = _Definitions(Path(__file__).parent / 'fixtures' / 'definitions')
mock_prepare_configs_dir = Path(__file__).parent / 'fixtures' / 'prepare_config'
