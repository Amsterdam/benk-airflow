import json
from pathlib import Path
from unittest.mock import Mock

import pytest


class TestDefinitions:

    def test_iter(self, model_definition):
        result = \
            {
              "catalog": "nap",
              "collections": [
                {
                  "collection": "peilmerken",
                  "workflows": [
                    {
                      "workflow": "import",
                      "arguments": {
                        "application": "Grondslag",
                        "mode": "full"
                      }
                    }
                  ]
                }
              ]
            }
        assert model_definition[0].json() == json.dumps(result)

    def test_iter_empty_folder(self, monkeypatch):
        with monkeypatch.context():
            monkeypatch.setattr("benk.definitions._Definitions._path", Path("/"))

            with pytest.raises(FileNotFoundError):
                from benk.definitions import DEFINITIONS
                list(DEFINITIONS)

    def test_workflow_handler(self, model_definition):
        model = model_definition[0]
        workflow = model.collections[0].workflows[0]
        assert workflow.handler.__name__ == workflow.workflow.title()

    def test_workflow_handler_error(self, model_definition, monkeypatch):
        model = model_definition[0]
        monkeypatch.setattr("importlib.import_module", Mock(side_effect=ImportError))

        with pytest.raises(ImportError, match="Workflow handler not found:"):
            model.collections[0].workflows[0].handler
