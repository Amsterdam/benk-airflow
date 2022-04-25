#!/usr/bin/env bash
# Configure the development environment
# Usage: source env.sh

if [ "$0" = "${BASH_SOURCE[0]}" ]; then
  echo "Run 'source ${BASH_SOURCE[0]}' to configure the environment."
  exit 1
fi

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DAGS_DIR=${PROJECT_DIR}/dags
echo "Configuring dags dir: ${DAGS_DIR}"

export PYTHONPATH=${PYTHONPATH}:${DAGS_DIR}
export AIRFLOW__CORE__DAGS_FOLDER=${DAGS_DIR}
export AIRFLOW__CORE__LOAD_EXAMPLES=False
