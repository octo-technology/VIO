ifneq (,$(wildcard .env))
	include .env
endif

SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:
.DEFAULT_GOAL: help

.EXPORT_ALL_VARIABLES:

CLOUD=azure/

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: deploy-vio-hub-azure  ## ⚙️ Deploy vio hub in Azure
deploy-vio-hub-azure:
	ansible-playbook $(CLOUD)/ansible/create_azure_cloud_infrastructure.yml

.PHONY: deploy-vio-hub-gcp  ## ⚙️ Deploy vio hub in Gcp
deploy-vio-hub-gcp:
	echo "Not implemented for the moment, coming soon..."

.PHONY: deploy-vio-hub-aws  ## ⚙️ Deploy vio hub in Aws
deploy-vio-hub-aws:
	echo "Not implemented for the moment, coming soon..."

.PHONY: deploy-hub-monitoring-azure  ## ⚙️ Deploy hub_monitoring files in Azure
deploy-hub-monitoring-azure:
	ssh-add $(CLOUD)/grafvio_id_rsa # chmod 400 deployment/grafvio_id_rsa
	ansible-playbook $(CLOUD)ansible/update_grafana_dashboard.yml  -i ansible/inventory --extra-vars ansible_port=22000
