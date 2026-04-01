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

.PHONY: install  ## ⏬ Install development dependencies
install:
	npm install

.PHONY: run_edge_interface  ## ✅ Launch the edge_interface app in development mode
run_edge_interface:
	npm run serve

.PHONY: start_edge_interface ## 🕵 Start edge_interface service (Docker container)
start_edge_interface:
	BUILDOS=${BUILDOS} docker compose --file edge_interface.yml up edge_interface -d --build

.PHONY: stop_edge_interface ## 🕵 Stop edge_interface service (Docker container)
stop_edge_interface:
	docker compose --file edge_interface.yml down edge_interface
