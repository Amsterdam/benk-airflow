# iBurgerZaken SFTP sync
Synchronizes all files found at the SFTP root to the GOB objectstore

## Steps
 - Build and tag docker image. We need the `paramiko` python package to be installed in our environment.
```bash
# kubernetes needs linux/amd64 platform, not arm for example
docker build --platform=linux/amd64 --tag=benkweuacrofkl2hn5eivwy.azurecr.io/iburgerzaken_sftp_sync:latest .
```

 - Log in to remote repository
```bash 
az acr login --name benkweuacrofkl2hn5eivwy
```

 - Push tagged image to remote repository
```bash
docker push benkweuacrofkl2hn5eivwy.azurecr.io/iburgerzaken_sftp_sync:latest
```

 - Set variables in airflow or make sure they are available in keyvault backend
   - SFTP_IBURGERZAKEN_UID
   - SFTP_IBURGERZAKEN_UID_PWD
   - DB_IBURGERZAKEN_SERVER
   - GOB_OBJECTSTORE_TENANTID
   - GOB_OBJECTSTORE_USER
   - GOB_OBJECTSTORE_PWD

- DAG should be visible in [Airflow](https://airflow-benkbbn1.dave-o.azure.amsterdam.nl/home), because of git-sync with the [benk-airflow repo](https://github.com/Amsterdam/benk-airflow).
- Trigger the DAG. This will pickup the image pushed to the ACR. 
- The files will be synced to: `development/iburgerzaken/<current timestamp>/` on the GOB objectstore.
