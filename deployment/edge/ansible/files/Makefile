SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:
BUILDOS=$(shell uname -s | tr '[:upper:]' '[:lower:]')


.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: edge_model_serving ## 💁 Start model_serving service (Docker container)
edge_model_serving:
	BUILDOS=${BUILDOS} docker compose up -d --build edge_model_serving

.PHONY: edge_orchestrator ## 🕵 Start edge_orchestrator service (Docker container)
edge_orchestrator:
	BUILDOS=${BUILDOS} docker compose up -d --build edge_orchestrator

.PHONY: edge_interface ## 📸 Start edge_interface inside a docker container
edge_interface:
	BUILDOS=${BUILDOS} docker compose up -d --build edge_interface

.PHONY: vio-edge-up ## 🐳 Start all edge services (db, model_serving, orchestrator, interface)
vio-edge-up:
	BUILDOS=${BUILDOS} docker compose --profile edge up -d --build

.PHONY: vio-down ## ❌ Stop all services (model_serving, edge_orchestrator, ui)
vio-down:
	docker compose --profile hub --profile edge down
