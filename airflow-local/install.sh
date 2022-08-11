#!/usr/bin/env bash
# Installs helm chart for airflow, with local dags dir mounted into it.
# Pods are started automatically after installation.
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DAGS_FOLDER=$(readlink -f "${SCRIPT_DIR}/../dags")
NAMESPACE="airflow"
cd "${SCRIPT_DIR}" || exit

# Create airflow namespace and configure volume to dynamically load DAGs from host
kubectl create namespace ${NAMESPACE}
DAGS_FOLDER_ESCAPED=$(printf '%s\n' "${DAGS_FOLDER}" | sed -e 's/[\/&]/\\&/g')
sed "s/##DAGS_FOLDER##/${DAGS_FOLDER_ESCAPED}/g" ./templates/volume.yaml.tpl \
  | kubectl apply --namespace ${NAMESPACE} -f -
kubectl apply --namespace ${NAMESPACE} -f "${SCRIPT_DIR}/templates/volume-claim.yaml"

# Create volumes shared between PodOperators. Unlike the previous volume, this
# uses a StorageClass. In development the StorageClass my-local-storage uses
# the node's host filesystem. In azure another StorageClass will be used, which
# mounts an Azure Storage Account.
mkdir -p "${SCRIPT_DIR}/shared-storage"
# Create StorageClass which binds as soon as it is used (WaitForFirstConsumer)
kubectl --namespace ${NAMESPACE} create -f "${SCRIPT_DIR}/templates/local-storage-class.yaml"
# Create a PersistentVolume, which is bound to the 'docker-desktop'-node
kubectl --namespace ${NAMESPACE} create -f "${SCRIPT_DIR}/templates/local-persistent-volume.yaml"
# Create a claim on that PV, which can be referenced from the DAG.
# The DAG contains a Volume which references to this claim.
# The PodOperator mounts that Volume on a given path.
kubectl --namespace ${NAMESPACE} create -f "${SCRIPT_DIR}/templates/local-persistent-volume-claim.yaml"

# Add apache airflow chart repository and install its helm chart
helm repo add apache-airflow https://airflow.apache.org
helm upgrade \
  --install airflow apache-airflow/airflow \
  --namespace ${NAMESPACE} \
  --create-namespace \
  --values="${SCRIPT_DIR}/values.yaml" \
  --debug

echo "Done"
echo "Forward ports: kubectl port-forward svc/airflow-webserver 8080:8080 --namespace ${NAMESPACE} > /dev/null 2>&1 &"
echo "Airflow dashboard: open http://localhost:8080"
