from benk.definitions import _Definitions
from pathlib import Path

mock_get_variable = type("MockVariable", (), {
    "get": lambda varname, *args, **kwargs: kwargs.get("default_var", f"resolved-{varname}")
})


mock_definitions = _Definitions(Path(__file__).parent / 'fixtures' / 'definitions')
mock_prepare_configs_dir = Path(__file__).parent / 'fixtures' / 'prepare_config'