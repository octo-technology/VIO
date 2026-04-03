ifneq (,$(wildcard .env))
	include .env
endif

SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:
.DEFAULT_GOAL: help

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: setup-secret-service-account  ## ⚙️ Setup secret service account for edge orchestrator
setup-secret-service-account:
	kubectl create secret generic service-account-credentials --from-file=key.json=$(PATH_TO_KEY_FILE)

.PHONY: setup-edge-vio  ## ⚙️ Setup edge for VIO
setup-edge-vio:
	kustomize build . | kubectl apply -f -
