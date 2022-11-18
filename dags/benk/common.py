import json
from datetime import timedelta

from airflow.models import Variable

default_args = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "email": ["ois.gob@amsterdam.nl"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
    "template_searchpath": ["/"],
    "user_defined_macros": {"json": json},
}

TEAM_NAME = "BenK"
NAMESPACE = Variable.get("pod-namespace", default_var="airflow")
REGISTRY_URL = Variable.get("pod-container-registry-url", default_var=None)
