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
