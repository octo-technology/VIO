SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:
LOCAL_VIO_DIR=$(shell git rev-parse --show-toplevel)

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: ping-inventory ## 🏓 Ping the edge devices describe in the inventory
ping-inventory:
	ansible all -i inventory.ini -m ping

.PHONY: deploy-vio-on-inventory ## 🚀 Deploy VIO on the edge devices describe in the inventory
deploy-vio-on-inventory:
	ansible-playbook -v -i inventory.ini deploy_vio_on_edge.yml
