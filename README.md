# Airflow Dags for BenK and GOB

This repository contains all code to run airflow dags from Basis en 
Kernregistraties. Mainly used to run GOB containers.

# Run local

## Kubernetes

### Kubernetes

Enable kubernetes in docker desktop.

preferences -> kubernetes -> Enable kubernetes

### Helm package manager

Install the helm package manager

```shell
brew install helm
```

### Install airflow in kubernetes

These commands take a while to complete.
```shell
helm repo add apache-airflow https://airflow.apache.org
helm upgrade \
  --install airflow apache-airflow/airflow \
  --namespace airflow \
  --create-namespace \
  --debug
```

Monitor progress on installing airflow:

```shell
kubectl get pods --namespace airflow
```

When done, all pods should display 'Running' or 'Completed' 

```
NAME                                 READY   STATUS    RESTARTS   AGE
airflow-postgresql-0                 1/1     Running   0          5m10s
airflow-redis-0                      1/1     Running   0          5m10s
airflow-scheduler-75b785f69c-srmgt   2/2     Running   0          5m10s
airflow-statsd-5bcb9dd76-c456f       1/1     Running   0          5m10s
airflow-triggerer-5ddcdcdfd9-m4gvn   1/1     Running   0          5m10s
airflow-webserver-85c4d647d4-qlbhv   1/1     Running   0          5m10s
airflow-worker-0                     2/2     Running   0          5m10s
```

Forward airflow admin interface port tot localhost:8080

```shell
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow &
```

Open http://localhost:8080 in your browser and login with:

- username: admin
- password: admin

# Development

## Dependencies
Before installing dependencies, a virtualenv is required.

```shell
pyenv virtualenv 3.10.1 benk-airflow
pyenv activate benk-airflow 
```

Install dependencies from _requirements-dev.txt_. This file includes _requirements.txt_. 

```shell
pip install -r requirements-dev.txt
```

## Code style

All python code should be formatted with black. To do this run:

```shell
./format.sh
```

## Mypy/flake8

Type checking is done with mypy.
In addition to `format.sh`, checking of code style is done with flake8.

Both commands are run with:

```shell
./test.sh
```
