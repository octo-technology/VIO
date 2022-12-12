SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:


.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: model_serving ## 💁 Start model_serving service (Docker container)
model_serving:
	docker-compose up -d --build model_serving

.PHONY: supervisor ## 🕵 Start supervisor service (Docker container)
supervisor:
	docker-compose up -d --build supervisor

.PHONY: edge_interface ## 📸 Start ui inside a docker container
edge_interface:
	docker-compose up -d --build edge_interface

.PHONY: mongodb ## 📁 Start mongodb inside a docker container
mongodb:
	docker-compose up -d --build mongodb

.PHONY: grafana-local ## ⚙️ Start grafana inside a docker container
grafana-local:
	docker-compose up -d --build grafana

.PHONY: deploy-grafana-azure ## ⚙️ Deploy grafana files in Azure
deploy-grafana-azure:
	ssh-add deployment/grafvio_id_rsa # chmod 400 deployment/grafvio_id_rsa
	ansible-playbook deployment/ansible/update_grafana_dashboard.yml  -i deployment/ansible/inventory --extra-vars ansible_port=22000

.PHONY: services-up ## 🐳 Start all services (mongodb, model_serving, supervisor, ui)
services-up:
	docker-compose up -d --build

.PHONY: services-up-raspberrypi ## 🐳 Start all services on RaspberryPI (mongodb, model_serving, supervisor, ui)
services-up-raspberrypi:
	docker-compose -f docker-compose.raspberrypi.yml up -d

.PHONY: services-down ## ❌ Stop all services (model_serving, supervisor, ui)
services-down:
	docker-compose down
