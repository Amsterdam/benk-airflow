import os
from datetime import timedelta
from pathlib import Path

from airflow.models import Variable

BaseOperaterArgs = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "email": ["ois.gob@amsterdam.nl"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}

TEAM_NAME = "BenK"
NAMESPACE = Variable.get("pod-namespace", default_var="airflow")
REGISTRY_URL = Variable.get("pod-container-registry-url", default_var=None)

AIRFLOW_HOME = Path(os.environ.get("AIRFLOW_HOME", "/opt/airflow"))
