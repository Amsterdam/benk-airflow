#!/usr/bin/env bash
# Installs helm chart for airflow, with local dags dir mounted into it.
# Pods are started automatically after installation.
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DAGS_FOLDER=$(readlink -f "${SCRIPT_DIR}/../dags")
NAMESPACE="airflow"
cd "${SCRIPT_DIR}" || exit

# Create airflow namespace and configure volumes
kubectl create namespace ${NAMESPACE}
DAGS_FOLDER_ESCAPED=$(printf '%s\n' "${DAGS_FOLDER}" | sed -e 's/[\/&]/\\&/g')
sed "s/##DAGS_FOLDER##/${DAGS_FOLDER_ESCAPED}/g" ./templates/volume.yaml.tpl \
  | kubectl apply --namespace ${NAMESPACE} -f -
kubectl apply --namespace ${NAMESPACE} -f "${SCRIPT_DIR}/templates/volume-claim.yaml"

# Add apache airflow chart repository and install its helm chart
helm repo add apache-airflow https://airflow.apache.org
helm upgrade \
  --install airflow apache-airflow/airflow \
  --namespace ${NAMESPACE} \
  --create-namespace \
  --values="${SCRIPT_DIR}/values.yaml" \
  --debug

echo "Done"
echo "Forward ports: kubectl port-forward svc/airflow-webserver 8080:8080 --namespace ${NAMESPACE} &"
echo "Airflow dashboard: open http://localhost:8080"
