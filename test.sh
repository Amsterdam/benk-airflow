#!/usr/bin/env bash
set -e

echo "Running mypy"
mypy dags/benk

echo "Running unit tests"
python -m pytest

echo "Check if black finds no potential reformat fixes"
black --check dags/benk

echo "Check for potential import sort"
isort --check --diff dags/benk

echo "Running flake8"
flake8 dags/benk

echo "Checks complete"
