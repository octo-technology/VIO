SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:


.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: edge_model_serving ## 💁 Start model_serving service (Docker container)
edge_model_serving:
	docker compose up -d --build edge_model_serving

.PHONY: edge_orchestrator ## 🕵 Start edge_orchestrator service (Docker container)
edge_orchestrator:
	docker compose up -d --build edge_orchestrator

.PHONY: edge_interface ## 📸 Start edge_interface inside a docker container
edge_interface:
	docker compose up -d --build edge_interface

.PHONY: edge_db ## 📁 Start edge_db inside a docker container
edge_db:
	docker compose up -d --build edge_db

.PHONY: hub_streamlit ## 🚀 Start hub_streamlit inside a docker container
hub_streamlit:
	docker compose up -d --build hub_streamlit

.PHONY: hub_monitoring ## 🚀 Start hub_monitoring inside a docker container
hub_monitoring:
	docker compose up -d --build hub_monitoring

.PHONY: hub_labelizer ## 🚀 Start hub_labelizer inside a docker container
hub_labelizer:
	docker compose up -d --build hub_labelizer

.PHONY: hub_monitoring_db ## 🚀 Start hub_monitoring database inside a docker container
hub_monitoring_db:
	docker compose up -d --build hub_monitoring_db

.PHONY: vio-hub-up ## 🐳 Start all hub services (monitoring, monitoring_db, labelizer)
vio-hub-up:
	docker compose --profile hub up -d --build

.PHONY: vio-edge-up ## 🐳 Start all edge services (db, model_serving, orchestrator, interface)
vio-edge-up:
	docker compose --profile edge up -d --build

.PHONY: vio-up ## 🐳 Start all edge services (db, model_serving, orchestrator, interface) and hubs (monitoring, monitoring_db, labelizer)
vio-up:
	docker compose --profile hub --profile edge up -d --build

.PHONY: vio-edge-up-raspberrypi ## 🐳 Start all edge services on RaspberryPI (db, model_serving, orchestrator, interface)
vio-edge-up-raspberrypi:
	docker compose -f docker-compose.raspberrypi.yml up -d --build

.PHONY: vio-down ## ❌ Stop all services (model_serving, edge_orchestrator, ui)
vio-down:
	docker compose --profile hub --profile edge down
