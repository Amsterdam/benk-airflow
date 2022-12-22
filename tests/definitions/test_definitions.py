import json
from pathlib import Path
from unittest import TestCase

from benk.definitions import _Definitions
from tests.mocks import mock_definitions


class TestDefinitions(TestCase):

    def test_iter(self):
        model_definition = list(mock_definitions)
        result = \
            {
                "catalog": "nap",
                "prepare": True,
                "collections": [
                    {
                        "collection": "peilmerken",
                        "import_": {
                            "application": "Grondslag"
                        },
                        "relations": [
                            "relation_attribute_1",
                            "relation_attribute_2",
                        ]
                    }
                ]
            }
        assert model_definition[0].json() == json.dumps(result)

    def test_iter_empty_folder(self):
        with self.assertRaises(FileNotFoundError):
            list(_Definitions(Path("/")))
