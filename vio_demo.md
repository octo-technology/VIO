# VIO demo - 10 juin 2023

## TODO
0. Merge kube MR
1. Setup edge intel ✅
   - connection wifi octo
   - pyenv for Python versions management
   - minikube installation
Prealable:
   - download service account files
     - tf-service-account
     - airbus-vio
2. Get edge informations for client questions ✅
2. Kube apply from edge terminal ✅
```shell
   kubectl create namespace vio
   kubectl config set-context --current --namespace=vio
```
   - [Creation d'une secret pour le docker-registry](https://support.count.ly/hc/en-us/articles/4698120212889-Docker-and-Kubernetes-Connecting-to-Private-Artifact-Registry-and-Pulling-Images-with-Authentication-Plugin-Packages) 
```shell
   kubectl create secret docker-registry artifact-registry \
   --docker-server=https://europe-west1-docker.pkg.dev \
   --docker-email=tf-service-account@acn-gcp-octo-sas.iam.gserviceaccount.com \
   --docker-username=_json_key \
   --docker-password="$(cat acn-gcp-octo-sas-dac2b63e6260.json)"
```
#### Troubleshooting

```shell
  error: Error loading config file "/etc/rancher/k3s/k3s.yaml": open /etc/rancher/k3s/k3s.yaml: permission denied
  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```
3. Setup camera ✅
4. Config VIO
4. Check data go to GCP
5. Train model with teachable machine (planche bois / vis) 
6. Export the model to quantise format tflite 
7. Integrate the model in vio-edge and test => create configuration
8. Deploy vio-edge on the edge with ansible from our macbook
9. Build grafana dashboard

### Connexion à l'edge 1

- ssh devkit@10.103.252.192

## Connexion SSH à un serveur

### Côté serveur
Check for `openssh-server` install:
```shell
$ man sshd_config
```
Si nothing shown

User
```shell
$ whoami
```

Hostname

⚠ hostname change everytime the server change network
```shell
$ hostname -I
```

### Coté client

Generate an ssh key
```shell
$ ssh-keygen
```

Add key identity to the authentication agent
```shell
$ ssh-add path_to_key
```

Check for server connection
```shell
$ ping hostname
```

Copy ssh key to server
```shell
$ ssh-copy-id -i path_to_key user@hostname
```

SSH on server
```shell
$ ssh user@hostname
```

### Minikube installation

```shell
$ kubectl version
$ docker version
$ export KUBECONFIG=~/.kube/config
$ mkdir ~/.kube 2> /dev/null
$ sudo k3s kubectl config view --raw > "$KUBECONFIG"
$ chmod 600 "$KUBECONFIG"
```

Add KUBECONFIG=~/.kube/config to ~/.bashrc
Fake model serving data

```
json_data = [
              {
                "x1": 0.29686468839645386,
                "y1": 0.5216227173805237,
                "x2": 0.3705231845378876,
                "y2": 0.5948795080184937,
                "confidence": 0.7182416915893555,
                "class": "wrinkle"
              },
              {
                "x1": 0.6872881054878235,
                "y1": 0.45187169313430786,
                "x2": 0.7481648325920105,
                "y2": 0.4979567527770996,
                "confidence": 0.598881185054779,
                "class": "wrinkle"
              }
            ]
```


VUE_APP_API_PROTOCOL=http
VUE_APP_API_HOSTNAME=edge-orchestrator.vio.svc.cluster.local
VUE_APP_API_PORT=8000