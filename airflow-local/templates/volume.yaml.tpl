apiVersion: v1
kind: PersistentVolume
metadata:
  name: dag-source-dir
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: ##DAGS_FOLDER##
