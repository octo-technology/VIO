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

.PHONY: conda_env  ## 🐍 Create a Python conda environment
conda_env:
	conda create --name tflite_serving python=3.7 -y

.PHONY: dependencies  ## ⏬ Install dependencies
dependencies:
	pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-macosx_10_14_x86_64.whl && pip install -r requirements.txt

.PHONY: dev-dependencies  ## ⏬ Install tests dependencies
dev-dependencies:
	pip install -r requirements-dev.txt

.PHONY: tests  ## ✅ Launch the unit tests
tests:
	pytest tests

.PHONY: tflite_serving  ## ✅ Launch the serving app
tflite_serving:
	uvicorn tflite_server:app --reload --port 8501 --host 0.0.0.0
