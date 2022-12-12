#!/usr/bin/env bash
set -e

# all configuration lives in pyproject.toml, except flake8 (.flake8)

echo "Running mypy"
mypy

echo "Running unit tests"
coverage run -m pytest

echo "Coverage report"
coverage report

echo "Check if black finds no potential reformat fixes"
black --check dags/benk

echo "Running flake8"
flake8 dags/benk
