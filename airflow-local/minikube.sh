LOCAL_SHARED_VOLUME="benk-airflow/shared-volume"
HOST_SHARED_VOLUME="/opt/shared-storage"

LOCAL_DAGS="benk-airflow/dags"
HOST_DAGS="/opt/airflow/dags"

LOCAL_PORT="8089"
NAMESPACE="airflow"

# remove cluster
sh ./remove.sh
minikube stop

# kill running mounts (kubectl and minikube)
pkill "kube"
clear

echo "Minikube version"
minikube update-check
sleep 2

# start cluster
minikube start

# add graphs
minikube addons enable metrics-server > /dev/null

# Mount shared volume
minikube mount $LOCAL_SHARED_VOLUME:$HOST_SHARED_VOLUME --uid=999 --gid=999 > /dev/null 2>&1 &

# mount dags
minikube mount $LOCAL_DAGS:$HOST_DAGS > /dev/null 2>&1 &

# opens browser
minikube dashboard > /dev/null 2>&1 &

# spin up airflow
echo "Installing Airflow..."
sh ./install.sh

# forward port aiflow web interface
echo "kubectl port-forward svc/airflow-webserver $LOCAL_PORT:8080 --namespace $NAMESPACE > /dev/null 2>&1 &"
kubectl port-forward svc/airflow-webserver "$LOCAL_PORT:8080" --namespace "$NAMESPACE" > /dev/null 2>&1 &
sleep 4

echo "Starting browser"
python3 -m webbrowser http://localhost:$LOCAL_PORT
