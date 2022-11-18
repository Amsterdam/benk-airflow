from airflow.models import Variable
from kubernetes.client import V1VolumeMount, V1Volume, V1PersistentVolumeClaimVolumeSource


class Volume:

    def __init__(self, name: str, mount_path: str, claim: str):
        self.name = name
        self.path = mount_path
        self.claim = claim

    @property
    def v1mount(self):
        return V1VolumeMount(
            name=self.name,
            mount_path=self.path,
            sub_path=None,
            read_only=False
        )

    @property
    def v1volume(self):
        pvc = V1PersistentVolumeClaimVolumeSource(claim_name=self.claim)
        return V1Volume(name=self.name, persistent_volume_claim=pvc)


GobVolume = Volume(
    name="gob-volume",
    mount_path="/app/shared",
    claim=Variable.get("pod-gob-shared-storage-claim", "shared-storage-claim")
)
