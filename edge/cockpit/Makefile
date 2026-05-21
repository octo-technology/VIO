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

.PHONY: install  ## ⏬ Install dependencies
install:
	npm install

.PHONY: docker-build  ## 🐳 Build the Docker image
docker-build:
	docker build -t ghcr.io/octo-technology/vio/edge_cockpit:latest .

.PHONY: docker-push  ## 📤 Push the Docker image to the registry
docker-push:
	docker push ghcr.io/octo-technology/vio/edge_cockpit:latest

.PHONY: serve  ## 🚀 Start dev server (proxies /api → localhost:8000)
serve:
	npm run dev

.PHONY: build  ## 📦 Build for production
build:
	npm run build

.PHONY: lint  ## 🐍 Lint Vue/JS files
lint:
	npm run lint

.PHONY: type_check  ## 🔎 TypeScript type check
type_check:
	npx tsc --noEmit

.PHONY: unit_tests  ## ✅ Launch unit tests
unit_tests:
	npm test
