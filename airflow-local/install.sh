#!/usr/bin/env bash
# Installs helm chart for airflow, with local dags dir mounted into it.
# Pods are started automatically after installation.
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DAGS_FOLDER=$(readlink -f "${SCRIPT_DIR}/../dags")
STORAGE_DIR=$(readlink -f "${SCRIPT_DIR}/shared-storage")
NAMESPACE="airflow"

# Returns an escaped directory.
#
# Arguments:
#    A path like "/path/to something", which will be escaped.
# Returns:
#    An escaped path "\/path\/to\ something"
escape_path() {
  local PATH_ARG=$1
  printf '%s\n' "${PATH_ARG}" | sed -e 's/[\/&]/\\&/g'
}

# Renders a single key in a templated yaml file.
#
# Variables in templates are formatted like: ##MY_VAR##
# TODO: this should be replaced with a helm chart.
#
# Arguments:
#    Path to a template
#    Template key to replace
#    Value to replace key with
# Returns:
#    A rendered template
render_template() {
  local TEMPLATE_PATH=$1
  local KEY=$2
  local VAL=$3
  sed "s/##${KEY}##/${VAL}/g" "${TEMPLATE_PATH}"
}

cd "${SCRIPT_DIR}" || exit

# Create airflow namespace and configure volume to dynamically load DAGs from host

kubectl create namespace ${NAMESPACE}
DAGS_FOLDER_ESCAPED=$(escape_path "${DAGS_FOLDER}")
TPL_VOLUME_RENDERED=$(render_template ./templates/volume.yaml.tpl "DAGS_FOLDER" "${DAGS_FOLDER_ESCAPED}")
echo "${TPL_VOLUME_RENDERED}" | kubectl apply --namespace ${NAMESPACE} -f -

kubectl apply --namespace ${NAMESPACE} -f "${SCRIPT_DIR}/templates/volume-claim.yaml"

# Create volumes shared between PodOperators. Unlike the previous volume, this
# uses a StorageClass. In development the StorageClass shared-storage uses
# the node's host filesystem. In azure another StorageClass will be used, which
# mounts an Azure Storage Account.
mkdir -p "${STORAGE_DIR}"
# Create StorageClass which binds as soon as it is used (WaitForFirstConsumer)
kubectl --namespace ${NAMESPACE} create -f "${SCRIPT_DIR}/templates/local-storage-class.yaml"
# Create a PersistentVolume, which is bound to the 'docker-desktop'-node
STORAGE_DIR_ESCAPED=$(escape_path "${STORAGE_DIR}")
TPL_LOCAL_PV_RENDERED=$(render_template ./templates/local-persistent-volume.yaml.tpl "STORAGE_DIRECTORY" "${STORAGE_DIR_ESCAPED}")
echo "$TPL_LOCAL_PV_RENDERED" | kubectl apply --namespace ${NAMESPACE} -f -

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
