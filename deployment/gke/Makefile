SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.EXPORT_ALL_VARIABLES:

REGION := europe-west1
PROJECT_ID := acn-gcp-octo-sas
ARTIFACT_REGISTRY := airbus-test


.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

get-docker-images:
	docker pull ghcr.io/octo-technology/vio/edge_interface:main
	docker pull ghcr.io/octo-technology/vio/edge_orchestrator:main

push-images-on-gcp-artifact:
	docker push $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACT_REGISTRY)/edge_interface:main
	docker push $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACT_REGISTRY)/edge_orchestrator:main

apply-front-gke-files:
	kubectl apply -f edge-interface/deployment.yaml
	kubectl apply -f edge-interface/service.yaml
	kubectl apply -f edge-interface/ingress.yaml

apply-api-gke-files:
	kubectl apply -f edge-orchestrator/deployment.yaml
	kubectl apply -f edge-orchestrator/service.yaml
	kubectl apply -f edge-orchestrator/ingress.yaml