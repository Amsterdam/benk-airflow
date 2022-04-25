# Airflow Dags for BenK

This repository contains all code to run airflow dags from Basis en 
Kernregistraties.

## Run local

### Installation
Before installing dependencies, a virtualenv is required.

```shell
pyenv virtualenv 3.10.1 benk-airflow
pyenv activate benk-airflow 
```

Install dependencies from _requirements-dev.txt_. This file includes _requirements.txt_. 

```shell
pip install -r requirements-dev.txt
```
### Configuration

#### Option 1: Configure Airflow environment

Source `env.sh` to configure airflow environment variables. 
Remember to source the variables on each terminal tab. 

```shell
source env.sh
```

#### Option 2: Configure Airflow configfile

__Note: the order of these steps is important.__

Set `dags_folder` in `~/airflow/airflow.cfg` to `/<FULL_PATH>/dags` in this repository. 

The example dags can be ignored: set `load_examples = False` in airflow.cfg

#### Initialize database tables

```shell
airflow db init
airflow dags list
```

The dags in this repository should appear.

## Development

### Code style

All code should be formatted with black. To do this run:

```shell
./format.sh
```

### Mypy/flake8

Type checking is done with mypy.
In addition to `format.sh`, checking of code style is done with flake8.
Both commands are run with:

```shell
./test.sh
```
