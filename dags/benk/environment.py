from typing import List

from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from kubernetes.client import V1EnvVar


class OperatorEnvironment:
    """Base environment class to put environment variables on.

    TODO: Use 'Secret' object for passwords instead.
    """

    def env_vars(self) -> List[V1EnvVar]:
        """Return all env vars in this object."""

        def _is_env_var(k) -> bool:
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


class GenericEnvironment(OperatorEnvironment):
    """Miscellaneous settings shared between containers"""

    GOB_SHARED_DIR = Variable.get("GOB-SHARED-DIR", "/app/shared")


class GOBEnvironment(OperatorEnvironment):
    """Settings to connect to connect to the GOB database.

    Note: this provides env vars for the dict 'GOB_DB' in config.py in
    gobupload and not in gobconfig. Gobconfig uses GOB_DATABASE_* as env var
    names, instead of DATABASE_*.
    """

    DATABASE_USER = Variable.get("DATABASE-USER", "gob")
    DATABASE_NAME = Variable.get("DATABASE-NAME", "gob")
    DATABASE_PASSWORD = Variable.get("DATABASE-PASSWORD")
    DATABASE_HOST_OVERRIDE = Variable.get(
        "DATABASE-HOST-OVERRIDE", "host.docker.internal"
    )
    DATABASE_PORT_OVERRIDE = Variable.get("DATABASE-PORT-OVERRIDE", "5406")


class GrondslagEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    GRONDSLAG_DATABASE_HOST = Variable.get("GRONDSLAG-DATABASE-HOST")
    GRONDSLAG_DATABASE_PASSWORD = Variable.get("GRONDSLAG-DATABASE-PASSWORD")
    GRONDSLAG_DATABASE = Variable.get("GRONDSLAG-DATABASE")
    GRONDSLAG_DATABASE_PORT = Variable.get("GRONDSLAG-DATABASE-PORT", "1521")
    GRONDSLAG_DATABASE_USER = Variable.get("GRONDSLAG-DATABASE-USER")
