# Airflow on local kubernetes

This is a Chart to run Airflow on kubernetes on development machines. 

The `../dags/` directory is mounted in pods, so that changes to dags are immediately 
available to the airflow instance.

# Install Airflow in local kubernetes

## Kubernetes

Enable kubernetes in docker desktop.

preferences -> kubernetes -> Enable kubernetes

## Helm package manager

Install the helm package manager

```shell
brew install helm
```
## Install Airflow

Install the chart from this directory. 
It installs airflow and configures the volumes to be mounted. 
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

Forward airflow admin interface port tot localhost:8080

```shell
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow &
```

Open http://localhost:8080 in your browser and login with:

- username: admin
- password: admin


## Remove airflow from kubernetes 
This removes the entire airflow namespace in kubernetes.

Additionally, it removes all volumes. 

```shell
./remove.sh
```
