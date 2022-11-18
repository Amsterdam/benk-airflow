from airflow.models import Variable

from benk.common import REGISTRY_URL


class Image:

    def __init__(self, name: str, tag: str):
        self.registry = REGISTRY_URL
        self.name = name
        self.tag = tag

    @property
    def pull_policy(self):
        # Pull policy 'Never' prevents importing from a remote repository.
        # This either uses a cached image or a locally built image.
        return "Never" if self.registry is None else "Always"

    @property
    def url(self):
        if self.registry is None:
            return f"{self.name}:{self.tag}"

        return f"{self.registry}/{self.name}:{self.tag}"


UploadImage = Image(
    name=Variable.get("pod-gob-upload-image-name", default_var="gob_upload"),
    tag=Variable.get("pod-gob-upload-image-tag", default_var="latest")
)

ImportImage = Image(
    name=Variable.get("pod-gob-import-image-name", default_var="gob_import"),
    tag=Variable.get("pod-gob-import-image-tag", default_var="latest")
)
