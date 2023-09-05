SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

# brew install openjdk

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: install
install:
	conda create --name pytorch python=3.9 -y
	conda activate pytorch
	conda install -c pytorch torchvision torchserve torch-model-archiver


.PHONY: download-models
download-models:
	wget https://download.pytorch.org/models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth
	mv fasterrcnn_resnet50_fpn_coco-258fb6c6.pth ../models/torch/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth


.PHONY: build-mar-file
build-mar-file:
	torch-model-archiver \
	--model-name fastrcnn \
	--version 1.0 \
	--model-file model.py \
	--serialized-file ../models/torch/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth \
	--handler object_detector \
	--extra-files ../models/torch/index_to_name.json -f

.PHONY: serve
serve:
	torchserve --start --model-store ../models/torch --models fastrcnn=fastrcnn.mar

.PHONY: test
test:
	curl http://127.0.0.1:8080/predictions/fastrcnn -T ..tests/data/persons.jpg
