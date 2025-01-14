SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: ping-edge ## 🏓 Ping the edge devices
ping-edge:
	ansible all -i inventory.ini -m ping

.PHONY: deploy-vio-on-edge ## 🚀 Deploy VIO on the edge devices
deploy-vio-on-edge:
	ansible-playbook -v -i inventory.ini deploy_vio_on_edge.yml

.PHONY: register-edge-on-gcp-hub ## 🚀 Register the edge devices on the GCP hub
register-edge-on-gcp-hub:
	ansible-playbook -v -i inventory.ini register_edge_on_gcp_hub.yml -e ansible_python_interpreter=.venv/bin/python

.PHONY: register-edge-on-gcp-hub-locally ## 🚀 Register the local edge device on the GCP hub
register-edge-on-gcp-hub-locally:
	ansible-playbook -v -c local -l edge_3 -i inventory.ini register_edge_on_gcp_hub.yml -e ansible_python_interpreter=.venv/bin/python
