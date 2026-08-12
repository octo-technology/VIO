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

.PHONY: edge_anomaly_serving ## 🔎 Start anomaly_serving anomaly detection service (Docker container)
edge_anomaly_serving:
	BUILDOS=${BUILDOS} docker compose up -d --build edge_anomaly_serving

.PHONY: edge_orchestrator ## 🕵 Start edge_orchestrator service (Docker container)
edge_orchestrator:
	BUILDOS=${BUILDOS} docker compose up -d --build edge_orchestrator

.PHONY: edge_cockpit ## 🖥 Start edge_cockpit inside a docker container
edge_cockpit:
	BUILDOS=${BUILDOS} docker compose up -d --build edge_cockpit

.PHONY: hub_streamlit ## 🚀 Start hub_streamlit inside a docker container
hub_streamlit:
	BUILDOS=${BUILDOS} docker compose up -d --build hub_streamlit

.PHONY: hub_labelizer ## 🚀 Start hub_labelizer inside a docker container
hub_labelizer:
	BUILDOS=${BUILDOS} docker compose up -d --build hub_labelizer

.PHONY: vio-hub-up ## 🐳 Build (if changed) and start all hub services
vio-hub-up:
	docker compose --profile hub up -d --build

.PHONY: vio-edge-up ## 🐳 Build (if changed) and start all edge services
vio-edge-up:
	docker compose --profile edge up -d --build

.PHONY: vio-up ## 🐳 Build (if changed) and start all services (edge + hub)
vio-up:
	docker compose --profile hub --profile edge up -d --build

.PHONY: install-tools ## 🔧 Install all edge services as uv tools (run once before vio-edge-local-up)
install-tools:
	uv tool install --editable edge/camera
	uv tool install --editable edge/tflite_serving
	uv tool install --editable edge/orchestrator
	cd edge/cockpit && npm install

.PHONY: vio-edge-local-up ## 💻 Start all edge services locally (no Docker, fake cameras)
vio-edge-local-up:
	lsof -ti :8000 -ti :8001 -ti :8501 -ti :3000 | xargs kill -9 2>/dev/null || true
	trap 'kill 0' SIGINT SIGTERM
	CAMERA_CONFIG_FILE=$(PWD)/edge/camera/camera_config.yml $(MAKE) -C edge/camera serve &
	MODELS_PATH=$(PWD)/edge/tflite_serving/models $(MAKE) -C edge/tflite_serving serve &
	CAMERA_SERVICE_URL=http://localhost:8001 SERVING_MODEL_URL=http://localhost:8501 CONFIG_DIR=$(PWD)/edge/orchestrator/config $(MAKE) -C edge/orchestrator serve &
	$(MAKE) -C edge/cockpit serve &
	wait

.PHONY: vio-down ## ❌ Stop all services (model_serving, edge_orchestrator, ui)
vio-down:
	docker compose --profile hub --profile edge down
