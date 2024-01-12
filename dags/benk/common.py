import datetime
from datetime import timedelta
from typing import Final

BaseOperaterArgs: Final = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "email": ["ois.gob@amsterdam.nl"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(seconds=300),
}

TEAM_NAME: Final = "BenK"
NAMESPACE: Final = "{{ var.value.get('pod-namespace', 'airflow') }}"
REGISTRY_URL: Final = "{{ var.value.get('pod-container-registry-url') }}"
AKS_NODE_POOL: Final = "benkbbn1work"

START_DATE = datetime.datetime(2023, 11, 1)
