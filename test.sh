#!/usr/bin/env bash
set -e
echo "Running mypy"
mypy dags/benk/

echo "Running flake8"
flake8 dags/

echo "Checking for valid python"
export PYTHONPATH=${PYTHONPATH}:dags/
python dags/benk/bag/dag.py
python dags/benk/nap/dag.py
