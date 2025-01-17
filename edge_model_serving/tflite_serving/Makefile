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

.PHONY: lint  ## 🐍 Lint Python files to conform to the PEP 8 style guide
lint:
	black .
	isort . --gitignore
	autoflake -i --remove-all-unused-imports -r --ignore-init-module-imports . --exclude .venv

.PHONY: check  ## 🐍 Check lint Python files to conform to the PEP 8 style guide
check:
	black . --check
	isort . --gitignore --check
	flake8 --count --show-source --statistics

.PHONY: autopep8  ## 🐍 Automatically formats Python code to conform to the PEP 8 style guide
autopep8:
	autopep8 --in-place --aggressive -r .

.PHONY: tflite_serving  ## 🐍 Create a tflite conda environment
tflite_serving:
	conda create --name tflite_serving python=3.8 -y

.PHONY: install_tflite_linux  ## ⏬ Install tflite development dependencies on linux
install_tflite_linux:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev,linux] && pip list --outdated

.PHONY: install_tflite_mac  ## ⏬ Install tflite development dependencies on mac
install_tflite_mac:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev] && pip list --outdated

.PHONY: tflite_tests  ## ✅ Launch the unit tflite_tests
tflite_tests:
	pytest -v --cov=src --junitxml=reports/tests-report.xml tests/

.PHONY: run_tflite_serving  ## ✅ Launch the tflite serving app
run_tflite_serving:
	uvicorn tflite_serving.tflite_server:app --reload --port 8501 --host 0.0.0.0
