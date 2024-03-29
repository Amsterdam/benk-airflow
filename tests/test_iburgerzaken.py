import unittest
from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from benk.common import BaseOperaterArgs


class TestIburgerZaken(unittest.TestCase):

    @freeze_time("2022-12-05")
    def test_iburgerzaken_dag(self):
        with (
            patch("airflow.DAG") as mock_dag,
            patch("airflow.providers.cncf.kubernetes.operators.kubernetes_pod.KubernetesPodOperator") as mock_operator,
            patch("benk.environment.IburgerZakenEnvironment") as mock_ibz_env
        ):
            import benk.iburgerzaken
            from benk.iburgerzaken import operator_default_args

            mock_dag.assert_called_with(
                dag_id="iburgerzaken",
                tags=["pink", "brp"],
                default_args=BaseOperaterArgs,
                catchup=False,
                start_date=datetime.utcnow(),
            )
            mock_operator.assert_called_with(
                name="sync_contents",
                task_id="sync_contents",
                namespace="{{ var.value.get('pod-namespace', 'airflow') }}",
                image="{{ var.value.get('pod-container-registry-url') }}"
                      "/"
                      "{{ var.value.get('pod-iburgerzaken-image-name', 'iburgerzaken-sftp-sync') }}"
                      ":"
                      "{{ var.value.get('pod-iburgerzaken-image-tag', 'latest') }}",
                image_pull_policy="Always",
                cmds=["python3"],
                arguments=["main.py"],
                env_vars=mock_ibz_env.return_value.env_vars.return_value,
                **operator_default_args
            )
