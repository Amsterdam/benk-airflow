from datetime import datetime
from unittest.mock import Mock

import pytest
from airflow import DAG
from airflow.models.baseoperator import BaseOperator

from benk.common import BaseOperaterArgs
import json
from freezegun import freeze_time


class TestGenerate:

    @freeze_time("2022-12-05")
    def test_generate(self, model_definition, monkeypatch):
        mock_dag = Mock(wraps=DAG)
        mock_dag.return_value.__enter__ = lambda x: True
        mock_dag.return_value.__exit__ = lambda *args: False
        monkeypatch.setattr("airflow.DAG", mock_dag)

        mock_chain = Mock(re=[1,2,3,4])
        monkeypatch.setattr("airflow.models.baseoperator.chain", mock_chain)

        # run generate DAG
        import benk.generate

        params = {
            "catalogue": "nap",
            "collection": "peilmerken",
            "application": "Grondslag",
            "mode": "full"
        }

        mock_dag.assert_called_with(
            dag_id="nap_peilmerken_Grondslag_full",
            params=params,
            tags=["import", "nap", "peilmerken", "Grondslag", "full"],
            default_args=BaseOperaterArgs,
            template_searchpath=["/"],
            user_defined_macros={"json": json},
            schedule_interval=None,
            catchup=False,
            start_date=datetime.utcnow(),
        )
        assert len(mock_chain.call_args_list[0][0][0]) == 5
        assert all(
            issubclass(type(task), BaseOperator) for task in mock_chain.call_args_list[0][0][0]
        )
