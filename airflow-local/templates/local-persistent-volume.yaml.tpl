apiVersion: v1
kind: PersistentVolume
metadata:
  name: shared-storage-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: shared-storage
  local:
    path: ##STORAGE_DIRECTORY##
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - docker-desktop
          - minikube
