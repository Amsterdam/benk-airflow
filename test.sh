#!/usr/bin/env bash
set -e
DAGS_PATH="dags/benk/"
export PYTHONPATH=${PYTHONPATH}:dags/

echo "Running mypy"
mypy "${DAGS_PATH}"

echo "Checking for valid python"
for FILE in "${DAGS_PATH}"*/**.py
do
  echo "Checking ${FILE}"
  python "${FILE}"
done

echo "Check if black finds no potential reformat fixes"
black --check ${DAGS_PATH}

echo "Running flake8"
flake8 dags/
