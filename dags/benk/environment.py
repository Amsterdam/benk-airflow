from typing import List

from airflow.utils.log.secrets_masker import mask_secret
from kubernetes.client import V1EnvVar


class OperatorEnvironment:
    """Base environment class to put environment variables on."""

    def env_vars(self) -> List[V1EnvVar]:
        """Return all env vars in this object."""
        secrets = []

        for key in dir(self):
            if key[:2] == "__" or callable(getattr(self, key)):
                continue

            secret = {key: getattr(self, key)}

            # https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/mask-sensitive-values.html
            # note: PWD is not masked, PASSWORD is
            mask_secret(secret)

            secrets.append(V1EnvVar(key, secret[key]))

        return secrets


class GenericEnvironment(OperatorEnvironment):
    """Miscellaneous settings shared between containers."""

    GOB_SHARED_DIR = "{{ var.value.get('gob-shared-dir', '/app/shared') }}"


class GOBEnvironment(OperatorEnvironment):
    """
    Settings to connect to connect to the GOB database.

    Note: this provides env vars for the dict 'GOB_DB' in config.py in
    gobupload and not in gobconfig. Gobconfig uses GOB_DATABASE_* as env var
    names, instead of DATABASE_*.
    """

    DATABASE_HOST_OVERRIDE = "{{ var.value.get('gob-database-host-override') }}"
    DATABASE_PASSWORD = "{{ var.value.get('gob-database-password') }}"
    DATABASE_NAME = "{{ var.value.get('gob-database-name') }}"
    DATABASE_PORT_OVERRIDE = "{{ var.value.get('gob-database-port-override') }}"
    DATABASE_USER = "{{ var.value.get('gob-database-user') }}"


class GrondslagEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    GRONDSLAG_DATABASE_HOST = "{{ var.value.get('grondslag-host') }}"
    GRONDSLAG_DATABASE_PASSWORD = "{{ var.value.get('grondslag-password') }}"
    GRONDSLAG_DATABASE = "{{ var.value.get('grondslag-db') }}"
    GRONDSLAG_DATABASE_PORT = "{{ var.value.get('grondslag-port') }}"
    GRONDSLAG_DATABASE_USER = "{{ var.value.get('grondslag-user') }}"


class DGDialogEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    BINBG_DATABASE_HOST = "{{ var.value.get('dgdialog-host') }}"
    BINBG_DATABASE_PASSWORD = "{{ var.value.get('dgdialog-password') }}"
    BINBG_DATABASE = "{{ var.value.get('dgdialog-db') }}"
    BINBG_DATABASE_PORT = "{{ var.value.get('dgdialog-port') }}"
    BINBG_DATABASE_USER = "{{ var.value.get('dgdialog-user') }}"


class ObjectStoreGOBEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    GOB_OBJECTSTORE_TENANT_ID = "{{ var.value.get('objectstore-gob-tenantid') }}"
    GOB_OBJECTSTORE_PASSWORD = "{{ var.value.get('objectstore-gob-password') }}"
    GOB_OBJECTSTORE_TENANT_NAME = "{{ var.value.get('objectstore-gob-tenantname') }}"
    GOB_OBJECTSTORE_USER = "{{ var.value.get('objectstore-gob-user') }}"


class ObjectStoreBasisInformatieEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the grondslag database."""

    BASISINFORMATIE_OBJECTSTORE_TENANT_ID = "{{ var.value.get('objectstore-bi-tenantid') }}"
    BASISINFORMATIE_OBJECTSTORE_PASSWORD = "{{ var.value.get('objectstore-bi-password') }}"
    BASISINFORMATIE_OBJECTSTORE_TENANT_NAME = "{{ var.value.get('objectstore-bi-tenantname') }}"
    BASISINFORMATIE_OBJECTSTORE_USER = "{{ var.value.get('objectstore-bi-user') }}"


class NeuronDatabaseEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the Neuron database."""

    NRBIN_DATABASE = "{{ var.value.get('neuron-database') }}"
    NRBIN_DATABASE_HOST = "{{ var.value.get('neuron-host') }}"
    NRBIN_DATABASE_PASSWORD = "{{ var.value.get('neuron-password') }}"
    NRBIN_DATABASE_PORT = "{{ var.value.get('neuron-port') }}"
    NRBIN_DATABASE_USER = "{{ var.value.get('neuron-user') }}"


class DecosDatabaseEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the Neuron database."""

    BINF_DATABASE = "{{ var.value.get('decos-database') }}"
    BINF_DATABASE_HOST = "{{ var.value.get('decos-host') }}"
    BINF_DATABASE_PASSWORD = "{{ var.value.get('decos-password') }}"
    BINF_DATABASE_PORT = "{{ var.value.get('decos-port') }}"
    BINF_DATABASE_USER = "{{ var.value.get('decos-user') }}"


class GOBPrepareDatabaseEnvironment(OperatorEnvironment):
    """Settings and secrets to connect to the GOB Prepare database."""

    GOB_PREPARE_DATABASE = "{{ var.value.get('gob-prepare-database') }}"
    GOB_PREPARE_DATABASE_HOST = "{{ var.value.get('gob-prepare-host') }}"
    GOB_PREPARE_DATABASE_PASSWORD = "{{ var.value.get('gob-prepare-password') }}"
    GOB_PREPARE_DATABASE_PORT = "{{ var.value.get('gob-prepare-port') }}"
    GOB_PREPARE_DATABASE_USER = "{{ var.value.get('gob-prepare-user') }}"


class PrepareServiceEnvironment(
    NeuronDatabaseEnvironment, GOBPrepareDatabaseEnvironment, ObjectStoreBasisInformatieEnvironment
):
    """All settings needed for the Prepare service to run."""

    pass


class IburgerZakenEnvironment(ObjectStoreGOBEnvironment):
    """Secrets used to connect to IBurgerZaken SFTP."""

    DB_IBURGERZAKEN_SERVER = "{{ var.value.get('db-iburgerzaken-server') }}"
    SFTP_IBURGERZAKEN_UID = "{{ var.value.get('sftp-iburgerzaken-uid') }}"
    SFTP_IBURGERZAKEN_UID_PASSWORD = "{{ var.value.get('sftp-iburgerzaken-uid-password') }}"
    SFTP_IBURGERZAKEN_PATH = "{{ var.value.get('sftp-iburgerzaken-path') }}"
