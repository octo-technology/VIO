SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.PHONY: help
help:
	echo "❓ Use \`make <target>\`"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: lint  ## 🐍 Lint Python files to conform to the PEP 8 style guide
lint:
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports . --exclude .venv
	isort . --skip-gitignore
	black .

.PHONY: check  ## 🐍 Check lint Python files to conform to the PEP 8 style guide
check:
	autoflake --in-place --remove-all-unused-imports --recursive --ignore-init-module-imports . --exclude .venv --check
	isort . --skip-gitignore --check
	black . --check
	flake8 --count --show-source --statistics

.PHONY: env ## Create a virtual environment
env:
	python3 -m venv env
	. env/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: run ## Run the streamlit app
run:
	streamlit run app.py --server.port 8502
