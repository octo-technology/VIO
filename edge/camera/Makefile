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

.PHONY: serve  ## 🚀 Run the camera service locally (CAMERA_BACKENDS=cam_1=fake by default)
serve:
	uv run uvicorn edge_camera.interface.api.app:create_app --factory \
		--host 0.0.0.0 --port 8001 --reload

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
