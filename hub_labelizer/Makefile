SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.EXPORT_ALL_VARIABLES:
.DEFAULT_GOAL: help

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
	autopep8 --in-place --aggressive -r hub_labelizer

.PHONY: conda_env  ## 🐍 Create a Python conda environment
conda_env:
	conda create --name hub_labelizer python=3.9 -y

.PHONY: install  ## ⏬ Install development dependencies
install:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev]
	pip list --outdated
