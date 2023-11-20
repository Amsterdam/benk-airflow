#!/usr/bin/env bash
echo "Running mypy"
mypy dags/benk

echo "Running black"
black dags/benk

echo "Running iSort"
isort dags/benk
