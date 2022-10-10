from typing import List, Any

from airflow.kubernetes.secret import Secret
from airflow.models import Variable
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from kubernetes.client import V1EnvVar


class EnvVariable(Variable):

    keyvault = SecretClient(
        vault_url=Variable.get("BENK_KEYVAULT_URL"),
        credential=ManagedIdentityCredential(client_id=Variable.get("BENK_AIRFLOW_CLIENTID"))
    )

    @classmethod
    def get(
        cls,
        key: str,
        default_var: Any = Variable.__NO_DEFAULT_SENTINEL,
        deserialize_json: bool = False,
        version: str = None
    ) -> Any:
        if secret := getattr(cls.keyvault.get_secret(key, version), "value", ""):
            return secret

        super().get(key, default_var, deserialize_json)


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

    GOB_SHARED_DIR = EnvVariable("GOB-SHARED-DIR", "/app/shared")


class GOBEnvironment(OperatorEnvironment):
    """Settings to connect to connect to the GOB database.

    Note: this provides env vars for the dict 'GOB_DB' in config.py in
    gobupload and not in gobconfig. Gobconfig uses GOB_DATABASE_* as env var
    names, instead of DATABASE_*.
    """
    DATABASE_USER = EnvVariable("DATABASE-USER", "gob")
    DATABASE_NAME = EnvVariable("DATABASE-NAME", "gob")
    DATABASE_PASSWORD = EnvVariable("DATABASE-PASSWORD")
    DATABASE_HOST_OVERRIDE = EnvVariable(
        "DATABASE-HOST-OVERRIDE", "host.docker.internal"
    )
    DATABASE_PORT_OVERRIDE = EnvVariable("DATABASE-PORT-OVERRIDE", "5406")


class GrondslagEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    GRONDSLAG_DATABASE_HOST = EnvVariable("GRONDSLAG-DATABASE-HOST")
    GRONDSLAG_DATABASE_PASSWORD = EnvVariable("GRONDSLAG-DATABASE-PASSWORD")
    GRONDSLAG_DATABASE = EnvVariable("GRONDSLAG-DATABASE")
    GRONDSLAG_DATABASE_PORT = EnvVariable("GRONDSLAG-DATABASE-PORT", "1521")
    GRONDSLAG_DATABASE_USER = EnvVariable("GRONDSLAG-DATABASE-USER")
