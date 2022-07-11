# Airflow Dags for BenK and GOB

This repository contains all code to run airflow dags from Basis en 
Kernregistraties. Mainly used to run GOB containers.

# Run on local kubernetes cluster

See [README.md](airflow-local/README.md) for installation instructions.

# Development

## Dependencies
Before installing dependencies, a virtualenv is required.

```shell
pyenv virtualenv 3.10.1 benk-airflow
pyenv activate benk-airflow 
```

Install dependencies from _requirements-dev.txt_. This file includes _requirements.txt_. 

```shell
pip install -r requirements-dev.txt
```

## Code style

All python code should be formatted with black. To do this run:

```shell
./format.sh
```

## Mypy/flake8

Type checking is done with mypy.
In addition to `format.sh`, checking of code style is done with flake8.

Both commands are run with:

```shell
./test.sh
```
