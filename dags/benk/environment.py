import dataclasses
from dataclasses import dataclass
from typing import Any

from airflow.models import Variable as AirflowVar
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from kubernetes.client import V1EnvVar


class EnvVar:

    keyvault = SecretClient(
        vault_url=AirflowVar.get("BENK_KEYVAULT_URL"),
        credential=ManagedIdentityCredential(client_id=AirflowVar.get("BENK_AIRFLOW_CLIENTID"))
    )

    def __init__(self, name: str, default_value: Any = None):
        self.name = name
        self.default_value = default_value

    def get(self) -> Any:
        if secret := getattr(self.keyvault.get_secret(self.name), "value", ""):
            return secret

        return AirflowVar.get(self.name) if self.default_value is None \
            else AirflowVar.get(self.name, self.default_value)

    def to_envvar(self, secret: Any) -> V1EnvVar:
        return V1EnvVar(name=secret, value=self.get())


@dataclass(frozen=True)
class GenericEnvironment:
    """Miscellaneous settings shared between containers"""

    GOB_SHARED_DIR = EnvVar("GOB-SHARED-DIR", "/app/shared")

    def env_vars(self) -> list[V1EnvVar]:
        return [env_var.to_envvar(secret) for secret, env_var in dataclasses.asdict(self).items()]


@dataclass(frozen=True)
class GOBEnvironment:
    """Settings to connect to connect to the GOB database.

    Note: this provides env vars for the dict 'GOB_DB' in config.py in
    gobupload and not in gobconfig. Gobconfig uses GOB_DATABASE_* as env var
    names, instead of DATABASE_*.
    """
    DATABASE_USER = EnvVar("DATABASE-USER", "gob")
    DATABASE_NAME = EnvVar("DATABASE-NAME", "gob")
    DATABASE_PASSWORD = EnvVar("DATABASE-PASSWORD")
    DATABASE_HOST_OVERRIDE = EnvVar(
        "DATABASE-HOST-OVERRIDE", "host.docker.internal"
    )
    DATABASE_PORT_OVERRIDE = EnvVar("DATABASE-PORT-OVERRIDE", "5406")


@dataclass(frozen=True)
class GrondslagEnvironment:
    """Settings and secrets to connect to the grondslag database."""

    GRONDSLAG_DATABASE_HOST = EnvVar("GRONDSLAG-DATABASE-HOST")
    GRONDSLAG_DATABASE_PASSWORD = EnvVar("GRONDSLAG-DATABASE-PASSWORD")
    GRONDSLAG_DATABASE = EnvVar("GRONDSLAG-DATABASE")
    GRONDSLAG_DATABASE_PORT = EnvVar("GRONDSLAG-DATABASE-PORT", "1521")
    GRONDSLAG_DATABASE_USER = EnvVar("GRONDSLAG-DATABASE-USER")


@dataclass(frozen=True)
class ImportEnvironment(GenericEnvironment, GrondslagEnvironment):
    pass


@dataclass(frozen=True)
class GobDbEnvironment(GenericEnvironment, GOBEnvironment):
    pass
