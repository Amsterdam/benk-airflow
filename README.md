# Airflow Dags for BenK and GOB

This repository contains all code to run airflow dags from Basis en 
Kernregistraties. Mainly used to run GOB containers.

# Run DAGs with Airflow on a local kubernetes cluster

See [README.md](airflow-local/README.md) for installation instructions.

# Development

## Containerised
This code is containerised, this works best. If you really, really want to be messing with virtual environments and
all that, install `requirements-dev.txt` with pip for local development.
But really, just use Docker.

## Code style

All python code should be formatted with black and isort. To do this run:

```shell
./format.sh
```

## Tests / mypy / flake8

Testing, type checking and format checks is done with `tests.sh`.
Type checking is done with mypy.
After checking of code style is done with flake8 and black.

```shell
docker compose build
docker compose up
```

# Airflow on Azure

## Configure DAGS with variables

Configure variables in the [GUI](https://airflow-benkbbn1.dave-o.azure.amsterdam.nl/variable/list/).
Configure secrets with the secrets pipeline.

Various variables need to be set.
Find variables in 'environment.py' in the dags directory.
Note that some configuration are variables and some are secrets.
Secrets need to be put in a keyvault, either in benk's or in dave's subscription.

Some important keys:
- AIRFLOW-POD-NAMESPACE: Namespace where airflow runs in DaVe's k8s cluster.
- CONTAINER-REGISTRY-URL: Url of registry of ACR in azure.
- GOB-IMPORT/UPLOAD-IMAGE-TAG: develop, or another branch name.
- GOB-IMPORT/UPLOAD-IMAGE-NAME: datapunt/gob_import, datapunt/gob_upload.
- GOB-SHARED-STORAGE-CLAIM: name of shared storage claim as given bij DaVe.

# Update prepare definitions

First update the GOB-Prepare git submodule:

    git submodule init
    git submodule update

Run from '''dags''' directory:

    python -m benk.prepare_config.update

This fetches the last versions of the prepare definitions from GitHub for the definitions marked with prepare: true