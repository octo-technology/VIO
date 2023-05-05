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
	--model-name yolo5 \
	--version 2.1 \
	--serialized-file ../models/torch/yolo5_v2.1.torchscript.pt \
	--handler ./torchserve_handler.py \
	--extra-files ../models/torch/index_to_name.json,./torchserve_handler.py

.PHONY: serve
serve:
	torchserve --start --model-store ../models/torch --models yolo=yolo5.mar

.PHONY: test
test:
	curl http://127.0.0.1:8080/predictions/yolo -T ../tests/L1\ front.jpg
