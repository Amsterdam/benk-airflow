#!/usr/bin/env bash
# Installs helm chart for airflow, with local dags dir mounted into it.
# Starts pods immediately.
# See README.md for more details on how to reach the airflow instance.
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DAGS_FOLDER=$(readlink -f "${SCRIPT_DIR}/../dags")
NAMESPACE="airflow"
cd "${SCRIPT_DIR}/.." || exit

echo "Current working directory: $(pwd)"

# Create airflow namespace and configure volumes
kubectl create namespace ${NAMESPACE}
kubectl apply --namespace ${NAMESPACE} -f "${SCRIPT_DIR}/templates"

# Add apache airflow chart repository and install it
helm repo add apache-airflow https://airflow.apache.org
helm upgrade \
  --install airflow apache-airflow/airflow \
  --namespace ${NAMESPACE} \
  --create-namespace \
  --values="${SCRIPT_DIR}/values.yaml" \
  --debug

echo "Done"
echo "Forward ports: kubectl port-forward svc/airflow-webserver 8080:8080 --namespace ${NAMESPACE} &"
echo "Open dashboard: open http://localhost:8080"
