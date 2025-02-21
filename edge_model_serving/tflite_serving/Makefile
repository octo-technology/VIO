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
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports src tests convert_pb_to_tflite.py --exclude .venv
	isort src tests convert_pb_to_tflite.py --skip-gitignore
	black src tests convert_pb_to_tflite.py

.PHONY: check  ## 🐍 Check lint Python files to conform to the PEP 8 style guide
check:
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports src tests convert_pb_to_tflite.py --exclude .venv --check
	isort src tests convert_pb_to_tflite.py --skip-gitignore --check
	black src tests convert_pb_to_tflite.py --check
	flake8 --count --show-source --statistics

.PHONY: tflite_serving  ## 🐍 Create a tflite conda environment
tflite_serving:
	conda create --name tflite_serving python=3.10 -y

.PHONY: install  ## ⏬ Install development dependencies
install:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev] && pip list --outdated

.PHONY: tflite_tests  ## ✅ Launch the unit tflite_tests
tflite_tests:
	pytest -v --cov=src --junitxml=reports/tests-report.xml tests/

.PHONY: run_tflite_serving  ## ✅ Launch the tflite serving app
run_tflite_serving:
	uvicorn tflite_serving.tflite_server:app --reload --port 8501 --host 0.0.0.0
