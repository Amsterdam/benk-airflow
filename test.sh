#!/usr/bin/env bash
set -e
DAGS_PATH="dags/benk/"
export PYTHONPATH=${PYTHONPATH}:dags/

echo "Running mypy"
mypy "${DAGS_PATH}"

echo "Running tests"
export COVERAGE_FILE=/tmp/.coverage

echo "Running unit tests"
coverage run --source=$DAGS_PATH -m pytest -s tests/

echo "Coverage report"
coverage report --show-missing --fail-under=100

echo "Check if black finds no potential reformat fixes"
black --check ${DAGS_PATH}

echo "Running flake8"
flake8 $DAGS_PATH
