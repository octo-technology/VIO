SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.EXPORT_ALL_VARIABLES:
.DEFAULT_GOAL: help

REPO_DIRECTORY:=$(shell pwd)
PYTHONPATH:=${PYTHONPATH}:${REPO_DIRECTORY}
BUILDOS=$(shell uname -s | tr '[:upper:]' '[:lower:]')

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: lint  ## 🐍 Lint and format Python files
lint:
	uv run --no-project ruff check --fix src tests
	uv run --no-project ruff format src tests

.PHONY: check  ## 🐍 Check lint and format (no changes)
check:
	uv run --no-project ruff check src tests
	uv run --no-project ruff format --check src tests

.PHONY: install  ## ⏬ Install development dependencies
install:
	uv venv && uv sync --group dev

.PHONY: update  ## ⬆️  Upgrade all dependencies to their latest allowed versions
update:
	uv sync --group dev

.PHONY: docker-build  ## 🐳 Build a multiplatform Docker image
docker-build:
	podman manifest rm edge-anomaly-serving 2>/dev/null || true
	podman build --platform linux/amd64,linux/arm64 --manifest edge-anomaly-serving .

.PHONY: docker-push  ## 📤 Build and push a multiplatform image to the registry
docker-push: docker-build
	podman manifest push --all edge-anomaly-serving docker://ghcr.io/octo-technology/vio/edge_anomaly_serving:latest

.PHONY: unit_tests  ## ✅ Launch the unit tests
unit_tests:
	uv run --no-project pytest -v --cov=src --junitxml=reports/tests-report.xml tests/

.PHONY: serve  ## 🚀 Run the RAD model server locally (port 8502)
serve:
	uv run --no-project uvicorn anomaly_serving.anomaly_server:app --host 0.0.0.0 --port 8502 --reload
