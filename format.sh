#!/usr/bin/env bash

echo "Running black"
black dags/benk

echo "Running iSort"
isort dags/benk
