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
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports . --exclude .venv
	isort . --skip-gitignore
	black .

.PHONY: check  ## 🐍 Check lint Python files to conform to the PEP 8 style guide
check:
	black . --check
	isort . --gitignore --check
	flake8 --count --show-source --statistics

.PHONY: conda_env  ## 🐍 Create a Python conda environment
conda_env:
	conda create --name hub_labelizer python=3.9 -y

.PHONY: install  ## ⏬ Install development dependencies
install:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev]
	pip list --outdated
