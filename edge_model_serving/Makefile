SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.EXPORT_ALL_VARIABLES:
REPO_DIRECTORY:=$(shell pwd)
PYTHONPATH:=${PYTHONPATH}:${REPO_DIRECTORY}

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

## tflite_serving

.PHONY: tflite_env  ## 🐍 Create a Python conda environment
tflite_env:
	conda create --name tflite_env python=3.8 -y

.PHONY: install_tflite_dependencies_linux  ## ⏬ Install tflite development dependencies on linux
install_tflite_dependencies_linux:
	python -m pip install --upgrade pip setuptools
	cd tflite_serving && pip install -e .[dev,linux] && pip list --outdated

.PHONY: install_tflite_dependencies_mac  ## ⏬ Install tflite development dependencies on mac
install_tflite_dependencies_mac:
	python -m pip install --upgrade pip setuptools
	cd tflite_serving && pip install -e .[dev,mac] && pip list --outdated

.PHONY: torch_env ## setup conda env
torch_env:
	conda create --name torch_env python=3.8 openssl=1.1.1n
	pip install -r torch_serving/requirements.txt

.PHONY: lint  ## 🐍 Lint Python files to conform to the PEP 8 style guide
lint:
	flake8 --count --show-source --statistics

.PHONY: autopep8  ## 🐍 Automatically formats Python code to conform to the PEP 8 style guide
autopep8:
	autopep8 --in-place --aggressive -r tflite_serving

.PHONY: tflite_tests  ## ✅ Launch the unit tflite_tests
tflite_tests:
	cd tflite_serving && pytest -v --cov=src --junitxml=reports/tests-report.xml tests/

.PHONY: edge_tflite_serving  ## ✅ Launch the serving app
edge_tflite_serving:
	cd tflite_serving && uvicorn tflite_serving.tflite_server:app --reload --port 8501 --host 0.0.0.0

.PHONY: edge_torch_serving  ## ✅ Launch the serving app
edge_torch_serving:
	cd torch_serving
	make download-models
	make build-mar-file
	make serve
