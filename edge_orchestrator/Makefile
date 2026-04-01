ifneq (,$(wildcard .env))
	include .env
endif

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
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports src tests --exclude .venv
	isort src tests --skip-gitignore
	black src tests

.PHONY: check  ## 🐍 Check lint Python files to conform to the PEP 8 style guide
check:
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports src tests --exclude .venv --check
	isort src tests --skip-gitignore --check
	black src tests --check
	flake8 --count --show-source --statistics src tests

.PHONY: conda_env  ## 🐍 Create a Python conda environment
conda_env:
	conda create --name edge_orchestrator python=3.9 -y

.PHONY: install  ## ⏬ Install development dependencies
install:
	python -m pip install --upgrade pip setuptools
	pip install -e .[dev]
	pip list --outdated

.PHONY: tests  ## ✅ Launch all the tests
tests: unit_tests integration_tests functional_tests

.PHONY: unit_tests  ## ✅ Launch the unit tests
unit_tests: REPORTS_PATH:=reports/pytest
unit_tests:
	echo "[*] Running unit tests and computing code coverage..."
	pytest -v --cov=src --cov-report=html:${REPORTS_PATH}/unit-tests-coverage \
		--junitxml=${REPORTS_PATH}/unit-tests-report.xml \
		tests/unit_tests
	echo "[*] Reports available in:"
	echo "👉 file://`pwd`/reports/pytest/unit-tests-report.xml"
	echo "👉 file://`pwd`/reports/pytest/coverage/index.html"

.PHONY: integration_tests  ## ✅ Launch the integration tests
integration_tests: REPORTS_PATH:=reports/pytest
integration_tests:
	echo "[*] Running integration tests and computing code coverage..."
	pytest -v --cov=src --cov-report=html:${REPORTS_PATH}/integration-tests-coverage \
		--junitxml=${REPORTS_PATH}/integration-tests-report.xml \
		tests/integration_tests
	echo "[*] Reports available in:"
	echo "👉 file://`pwd`/reports/pytest/integration-tests-report.html"
	echo "👉 file://`pwd`/reports/pytest/coverage/index.html"

.PHONY: functional_tests  ## ✅ Launch the functional tests
functional_tests: REPORTS_PATH:=reports/pytest
functional_tests:
	behave

.PHONY: pyramid  ## ⨺ Compute the tests pyramid
pyramid:
	python tests/tests_pyramid.py --no-badges-generation

.PHONY: pyramid_and_badges  ## 📛 Generate Gitlab badges
pyramid_and_badges:
	python tests/tests_pyramid.py --badges-generation

.PHONY: serve  ## 🚀 Run the orchestrator locally (port 8000)
serve:
	uvicorn edge_orchestrator.interface.api.main:app --host 0.0.0.0 --port 8000 --reload
