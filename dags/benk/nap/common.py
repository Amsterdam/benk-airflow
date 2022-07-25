from datetime import datetime, timedelta
from typing import Optional, Tuple

default_args = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "start_date": datetime.utcnow(),
    "email": ["gob.ois@amsterdam.nl"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}


def get_image_url(
    registry_url: Optional[str], image_name: str, tag: str
) -> Tuple[str, str]:
    """Use a remote image, or a cached image if no URL is given.

    :param registry_url: URL of the container registry, None if local image is desired.
    :param image_name: name of the image.
    :param tag: tag of the image.
    :return: A tuple with pull policy and a URL.
    """
    if registry_url is None:
        # Pull policy 'Never' prevents importing from a remote repository.
        # This either uses a cached image or a locally built image.
        return "Never", f"{image_name}:{tag}"

    # Pull policy Always forces pulling the latest image from a remote registry.
    return "Always", f"{registry_url}/{image_name}:{tag}"
