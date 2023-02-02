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
	conda create --name edge_tflite_serving python=3.7 -y
	pip install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-macosx_10_14_x86_64.whl && pip install -r requirements.txt
	pip install -r requirements-dev.txt

.PHONY: torch_env ## setup conda env
torch_env:
	conda create -n pytorchenv python=3.8 openssl=1.1.1n
	conda install pytorch torchvision torchserve torch-model-archiver -c pytorch
	pip install -r requirements.txt
	conda activate torchenv

.PHONY: lint  ## 🐍 Lint Python files to conform to the PEP 8 style guide
lint:
	flake8 --count --show-source --statistics --exclude venv*

.PHONY: autopep8  ## 🐍 Automatically formats Python code to conform to the PEP 8 style guide
autopep8:
	autopep8 --in-place --aggressive -r tflite_serving

.PHONY: tests  ## ✅ Launch the unit tests
tests:
	pytest tests

.PHONY: edge_tflite_serving  ## ✅ Launch the serving app
edge_tflite_serving:
	cd tflite_serving/src
	uvicorn tflite_server:app --reload --port 8501 --host 0.0.0.0

.PHONY: edge_torch_serving  ## ✅ Launch the serving app
edge_torch_serving:
	cd torch_serving/src
	uvicorn fast_serving:app --reload --port 8501 --host 0.0.0.0
