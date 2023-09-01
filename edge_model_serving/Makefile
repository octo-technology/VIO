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
	flake8 --count --show-source --statistics
	black . --check

.PHONY: autopep8  ## 🐍 Automatically formats Python code to conform to the PEP 8 style guide
autopep8:
	autopep8 --in-place --aggressive -r .
