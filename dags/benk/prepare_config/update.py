"""To update the prepare definitions in this directory, run from 'dags' directory.

python -m benk.prepare_config.update

"""

from pathlib import Path

import requests

from benk.definitions import DEFINITIONS

GITHUB_BASE_URL = "https://raw.githubusercontent.com/Amsterdam/GOB-Prepare/master"


def _update_for_catalogue(catalogue: str):
    r = requests.get(
        f'{GITHUB_BASE_URL}/src/data/{catalogue}.prepare.json')
    r.raise_for_status()

    with open(Path(__file__).parent / f'{catalogue}.prepare.json', 'w') as f:
        f.write(r.text)


def update():
    """Update the prepare configurations in the prepare_config directory for the prepare-enabled definitions."""
    for definition in DEFINITIONS:
        if definition.prepare:
            print(f"Updating prepare definition for {definition.catalog}")
            _update_for_catalogue(definition.catalog)


if __name__ == "__main__":
    update()  # pragma: no cover
