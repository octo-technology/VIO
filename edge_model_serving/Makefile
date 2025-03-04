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

.PHONY: lint  ## 🐍 Lint Python files to conform to the PEP 8 style guide
lint:
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports src --exclude .venv
	isort src --skip-gitignore
	black src

.PHONY: check  ## 🐍 Check lint Python files to conform to the PEP 8 style guide
check:
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports src --exclude .venv --check
	isort src --skip-gitignore --check
	black src --check
	flake8 --count --show-source --statistics

.PHONY: install  ## ⏬ Install development dependencies
install:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev] && pip list --outdated

.PHONY: run_tflite_serving  ## ✅ Launch the tflite serving app
run_tflite_serving:
	uvicorn tflite_serving.tflite_server:app --reload --port 8501 --host 0.0.0.0

.PHONY: start_edge_model_serving ## 🕵 Start edge_model_serving service (Docker container)
start_edge_model_serving:
	BUILDOS=${BUILDOS} docker compose --file edge_model_serving.yml up edge_model_serving -d --build

.PHONY: stop_edge_model_serving ## 🕵 Stop edge_model_serving service (Docker container)
stop_edge_model_serving:
	docker compose --file edge_model_serving.yml down edge_model_serving
