# Airflow on local Kubernetes

This is a Helm chart to run Airflow on Kubernetes on development machines.

The `../dags/` directory is mounted in pods, so that changes to dags are immediately available to the Airflow instance.

# Install Airflow in local Kubernetes

## Prerequisites

Requires docker to run on your development machine. 
Images are pulled from your local registry, so it is best to build all GOB-* images first. 

## Kubernetes

Enable Kubernetes in Docker Desktop:

*Preferences -> Kubernetes -> Enable Kubernetes*

## Helm package manager

Install the Helm package manager:

```shell
brew install helm
```

## Install Airflow

Install the chart from this directory.
It installs Airflow and configures the volumes to be mounted.
These commands take a while to complete.

```shell
./install.sh
```

When done, all pods should display 'Running' or 'Completed'.

```shell
kubectl get pods --namespace airflow
```

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

Forward Airflow UI port to localhost:8080:

```shell
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow &
```

Open [localhost:8080](http://localhost:8080) in your browser and login with:

- username: `admin`
- password: `admin`

### Configure DAGS with variables

These variables are suitable to run the dags locally.

Configure TEST variable in the [GUI](http://localhost:8080/variable/list/).

Or click import variables and load variables.json.

## Remove Airflow from Kubernetes
This removes the entire Airflow namespace in Kubernetes.

Additionally, it removes all volumes.

```shell
./remove.sh
```
