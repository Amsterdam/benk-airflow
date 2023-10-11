from datetime import timedelta

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
NAMESPACE = "{{ var.value.get('pod-namespace', 'airflow') }}"
REGISTRY_URL = "{{ var.value.get('pod-container-registry-url') }}"
