from datetime import datetime, timedelta
from typing import Optional

default_args = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "start_date": datetime.utcnow(),
    "email": ["ois.gob@amsterdam.nl"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}


def get_image_url(registry_url: Optional[str], image_name: str, tag: str) -> str:
    """Use a remote image, or a cached image if no URL is given.

    :param registry_url: URL of the container registry, None if local image is desired.
    :param image_name: name of the image.
    :param tag: tag of the image.
    :return: An URL to an image, or just an image name.
    """
    if registry_url is None:
        return f"{image_name}:{tag}"

    return f"{registry_url}/{image_name}:{tag}"


def get_image_pull_policy(registry_url: Optional[str]) -> str:
    """Return desired image pull policy.

    Docs:
        https://kubernetes.io/docs/concepts/containers/images/
        image_pull_policy: "Never", "Always" (, "IfNotPresent")

    :param registry_url: URL of the container registry, None if local image is desired.
    :return: A string with the pull policy (Always, Never)
    """
    if registry_url is None:
        # Pull policy 'Never' prevents importing from a remote repository.
        # This either uses a cached image or a locally built image.
        return "Never"

    # Pull policy Always forces pulling the latest image from a remote registry.
    return "Always"
