#!/usr/bin/env bash
kubectl delete ns airflow
kubectl delete pvc dag-source-dir-claim
kubectl delete pv dag-source-dir
echo "Removed airflow and volumes."
