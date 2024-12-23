## Launch edge locally and upload data on GCP

### Service account for edge_orchestrator
- Create a service account with the roles/storage.admin directly through the GCP UI.
- Export key json file
- Store the key file at this location: `edge_orchestrator/config/secrets/credentials.json`

### Set env variables on docker-compose.yml

    API_CONFIG: upload-gcp
    GOOGLE_APPLICATION_CREDENTIALS: /edge_orchestrator/config/secrets/credentials.json
    GCP_BUCKET_NAME: <bucket-name>

### Launch VIO
```shell
$ make edge_orchestrator
```

## Deploy edge on GCP via Kube

Ensure that Terraform has ran before to create the infrastructure.

### Service account for edge_orchestrator
- Create a service account with the roles/storage.admin
- Export key json file

#### Create secret edge_orchestrator service account
```shell
$ make setup-secret-service-account PATH_TO_KEY_FILE=file.json 
```

### Run kustomize for deploy kube files

#### Install kustomize
```shell
$ curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
$ sudo install -o root -g root -m 0755 kustomize /usr/local/bin/kustomize
```
#### Deploy VIO
```shell
$ make setup-edge-vio
```
