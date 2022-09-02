#!/usr/bin/env bash
kubectl delete ns airflow
kubectl delete pvc dag-source-dir-claim
kubectl delete pv dag-source-dir
kubectl delete pvc shared-storage-claim
kubectl delete pv shared-storage-pv
kubectl delete storageclasses.storage.k8s.io shared-storage

echo "Removed airflow and volumes."
