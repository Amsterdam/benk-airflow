from benk.common import REGISTRY_URL


class Image:
    def __init__(self, name: str, tag: str):
        self.name = name
        self.tag = tag

    @property
    def pull_policy(self):
        # Pull policy 'Never' prevents importing from a remote repository.
        # This either uses a cached image or a locally built image.
        return "Never" if REGISTRY_URL is None else "Always"

    @property
    def url(self):
        if REGISTRY_URL is None:
            return f"{self.name}:{self.tag}"

        return f"{REGISTRY_URL}/{self.name}:{self.tag}"
