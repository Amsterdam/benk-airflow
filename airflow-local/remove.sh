#!/usr/bin/env bash
kubectl delete ns airflow
kubectl delete pvc dag-source-dir-claim
kubectl delete pv dag-source-dir
kubectl delete pvc my-claim
kubectl delete pv my-local-pv
kubectl delete storageclasses.storage.k8s.io my-local-storage

echo "Removed airflow and volumes."
