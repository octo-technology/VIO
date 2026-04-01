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

.PHONY: lint  ## 🐍 Lint and format Python files
lint:
	uv run ruff check --fix src tests
	uv run ruff format src tests

.PHONY: check  ## 🐍 Check lint and format (no changes)
check:
	uv run ruff check src tests
	uv run ruff format --check src tests

.PHONY: install  ## ⏬ Install development dependencies
install:
	uv pip install -e ".[dev]"

.PHONY: tests  ## ✅ Launch all the tests
tests: unit_tests integration_tests functional_tests

.PHONY: unit_tests  ## ✅ Launch the unit tests
unit_tests: REPORTS_PATH:=reports/pytest
unit_tests:
	echo "[*] Running unit tests and computing code coverage..."
	uv run pytest -v --cov=src --cov-report=html:${REPORTS_PATH}/unit-tests-coverage \
		--junitxml=${REPORTS_PATH}/unit-tests-report.xml \
		tests/unit_tests
	echo "[*] Reports available in:"
	echo "👉 file://`pwd`/reports/pytest/unit-tests-report.xml"
	echo "👉 file://`pwd`/reports/pytest/coverage/index.html"

.PHONY: integration_tests  ## ✅ Launch the integration tests
integration_tests: REPORTS_PATH:=reports/pytest
integration_tests:
	echo "[*] Running integration tests and computing code coverage..."
	uv run pytest -v --cov=src --cov-report=html:${REPORTS_PATH}/integration-tests-coverage \
		--junitxml=${REPORTS_PATH}/integration-tests-report.xml \
		tests/integration_tests
	echo "[*] Reports available in:"
	echo "👉 file://`pwd`/reports/pytest/integration-tests-report.html"
	echo "👉 file://`pwd`/reports/pytest/coverage/index.html"

.PHONY: functional_tests  ## ✅ Launch the functional tests
functional_tests: REPORTS_PATH:=reports/pytest
functional_tests:
	uv run behave

.PHONY: pyramid  ## ⨺ Compute the tests pyramid
pyramid:
	uv run python tests/tests_pyramid.py --no-badges-generation

.PHONY: pyramid_and_badges  ## 📛 Generate Gitlab badges
pyramid_and_badges:
	uv run python tests/tests_pyramid.py --badges-generation

.PHONY: serve  ## 🚀 Run the orchestrator locally (port 8000)
serve:
	uv run uvicorn edge_orchestrator.interface.api.main:app --host 0.0.0.0 --port 8000 --reload
