SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.EXPORT_ALL_VARIABLES:
.DEFAULT_GOAL: help

REPO_DIRECTORY:=$(shell pwd)
PYTHONPATH:=${PYTHONPATH}:${REPO_DIRECTORY}

help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'


.PHONY: lint  ## 🐍 Lint Python files to conform to the PEP 8 style guide
lint:
	flake8 --count --show-source --statistics --exclude venv*

.PHONY: autopep8  ## 🐍 Automatically formats Python code to conform to the PEP 8 style guide
autopep8:
	autopep8 --in-place --aggressive -r supervisor

.PHONY: conda_env  ## 🐍 Create a Python conda environment
conda_env:
	conda create --name supervisor python=3.9 -y

.PHONY: install  ## ⏬ Install development dependencies
install:
	python -m pip install --upgrade pip
	pip install -e .[dev]
	pip list --outdated

.PHONY: tests  ## ✅ Launch all the tests
tests: unit_tests integration_tests functional_tests
	coverage combine

.PHONY: unit_tests  ## ✅ Launch the unit tests
unit_tests: REPORTS_PATH:=reports/pytest
unit_tests:
	echo "[*] Running unit tests and computing code coverage..."
	pytest -v --cov=supervisor --cov-report=html:${REPORTS_PATH}/coverage \
		--junitxml=${REPORTS_PATH}/unit-tests-report.xml \
		tests/unit_tests
	echo "[*] Reports available in:"
	echo "👉 file://`pwd`/reports/pytest/unit-tests-report.xml"
	echo "👉 file://`pwd`/reports/pytest/coverage/index.html"

.PHONY: integration_tests  ## ✅ Launch the integration tests
integration_tests: REPORTS_PATH:=reports/pytest
integration_tests:
	echo "[*] Running integration tests and computing code coverage..."
	pytest -v --cov=supervisor --cov-report=html:${REPORTS_PATH}/coverage \
		--junitxml=${REPORTS_PATH}/integration-tests-report.xml \
		tests/integration_tests
	echo "[*] Reports available in:"
	echo "👉 file://`pwd`/reports/pytest/integration-tests-report.html"
	echo "👉 file://`pwd`/reports/pytest/coverage/index.html"
	COVERAGE_FILE=.coverage.integration_tests API_CONFIG=test coverage run --omit 'venv/*,tests/*' -m pytest tests/integration_tests

.PHONY: functional_tests  ## ✅ Launch the functional tests
functional_tests: REPORTS_PATH:=reports/pytest
functional_tests:
	COVERAGE_FILE=${REPORTS_PATH}/coverage.functional_tests API_CONFIG=test coverage run --omit 'venv/*,tests/*' -m behave

.PHONY: pyramid  ## ⨺ Compute the tests pyramid
pyramid:
	python tests/tests_pyramid.py --no-badges-generation

.PHONY: pyramid_and_badges  ## 📛 Generate Gitlab badges
pyramid_and_badges:
	python tests/tests_pyramid.py --badges-generation
