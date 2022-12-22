"""To update the prepare definitions in this directory, run from 'dags' directory.

python -m benk.prepare_config.update

"""

import shutil
from pathlib import Path

from benk.definitions import DEFINITIONS

PREPARE_DATA_DIR = Path(__file__).parent.parent.parent / 'GOB-Prepare' / 'src' / 'data'


def _update_for_catalogue(catalogue: str):
    fname = f'{catalogue}.prepare.json'
    src_file = PREPARE_DATA_DIR / fname
    dst_file = Path(__file__).parent / fname

    shutil.copyfile(src_file, dst_file)


def update():
    """Update the prepare configurations in the prepare_config directory for the prepare-enabled definitions."""
    for definition in DEFINITIONS:
        if definition.prepare:
            print(f"Updating prepare definition for {definition.catalog}")
            _update_for_catalogue(definition.catalog)


if __name__ == "__main__":
    update()  # pragma: no cover
