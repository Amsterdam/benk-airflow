#!/usr/bin/env bash
set -e
DAGS_PATH="dags/benk/"
export PYTHONPATH=${PYTHONPATH}:dags/

echo "Running mypy"
mypy "${DAGS_PATH}"

echo "Running tests"
pytest -s tests/

echo "Check if black finds no potential reformat fixes"
black --check ${DAGS_PATH}

echo "Running flake8"
flake8 dags/
