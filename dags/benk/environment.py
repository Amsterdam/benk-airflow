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
    DATABASE_USER = Variable.get("gob-database-user", "gob")
    DATABASE_NAME = Variable.get("gob-database-name", "gob")
    DATABASE_PASSWORD = Variable.get("gob-database-password")
    DATABASE_HOST_OVERRIDE = Variable.get(
        "gob-database-host-override", "host.docker.internal"
    )
    DATABASE_PORT_OVERRIDE = Variable.get("gob-database-port-override", "5406")


class GrondslagEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    GRONDSLAG_DATABASE_HOST = Variable.get("grondslag-host")
    GRONDSLAG_DATABASE_PASSWORD = Variable.get("grondslag-password")
    GRONDSLAG_DATABASE = Variable.get("grondslag-db")
    GRONDSLAG_DATABASE_PORT = Variable.get("grondslag-port", "1521")
    GRONDSLAG_DATABASE_USER = Variable.get("grondslag-user")


class DGDialogEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    BINBG_DATABASE_HOST = Variable.get("dgdialog-host")
    BINBG_DATABASE_PASSWORD = Variable.get("dgdialog-password")
    BINBG_DATABASE = Variable.get("dgdialog-db")
    BINBG_DATABASE_PORT = Variable.get("dgdialog-port", "1521")
    BINBG_DATABASE_USER = Variable.get("dgdialog-user")


class ObjectStoreGOBEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    GOB_OBJECTSTORE_TENANT_ID = Variable.get("objectstore-gob-tenantid")
    GOB_OBJECTSTORE_PASSWORD = Variable.get("objectstore-gob-password")
    GOB_OBJECTSTORE_TENANT_NAME = Variable.get("objectstore-gob-tenantname")
    GOB_OBJECTSTORE_USER = Variable.get("objectstore-gob-user")


class ObjectStoreBasisInformatieEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    BASISINFORMATIE_OBJECTSTORE_TENANT_ID = Variable.get("objectstore-bi-tenantid")
    BASISINFORMATIE_OBJECTSTORE_PASSWORD = Variable.get("objectstore-bi-password")
    BASISINFORMATIE_OBJECTSTORE_TENANT_NAME = Variable.get("objectstore-bi-tenantname")
    BASISINFORMATIE_OBJECTSTORE_USER = Variable.get("objectstore-bi-user")
