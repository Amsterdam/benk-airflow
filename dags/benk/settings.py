from typing import List

from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from kubernetes.client import V1EnvVar


class Settings:
    """Contains global settings and secrets for all tasks.

    TODO: Use 'Secret' object for passwords instead.
    """

    GRONDSLAG_DATABASE_HOST = Variable.get(
        "GRONDSLAG_DATABASE_HOST", default_var="DBEXTA1LORA2.ACC.AMSTERDAM.NL"
    )
    GRONDSLAG_DATABASE_PASSWORD = Variable.get("GRONDSLAG_DATABASE_PASSWORD")
    GRONDSLAG_DATABASE = Variable.get("GRONDSLAG_DATABASE", default_var="NAPGR1TA_APP")
    GRONDSLAG_DATABASE_PORT = Variable.get(
        "GRONDSLAG_DATABASE_PORT", default_var="1521"
    )
    GRONDSLAG_DATABASE_USER = Variable.get(
        "GRONDSLAG_DATABASE_USER", default_var="grondslag_proxy"
    )

    def env_vars(self) -> List[V1EnvVar]:
        """Returns all env vars in this object"""

        def _is_env_var(k):
            if str(k).startswith("__"):
                return False
            if isinstance(getattr(self, k), Secret):
                return False
            if callable(getattr(self, k)):
                return False
            return True

        return [
            V1EnvVar(name=k, value=getattr(self, k))
            for k in dir(self)
            if _is_env_var(k)
        ]
