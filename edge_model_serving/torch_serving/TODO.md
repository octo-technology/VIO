- with model-file model.py
- checkpoints

how to avoid Downloading: "https://download.pytorch.org/models/vgg16-397923af.pth"


.PHONY: build-mar-file
build-mar-file:
	torch-model-archiver \
	--model-name ols-smart-rack \
    --model-file model.py
	--version 1.0 \
	--serialized-file ./trained_models/checkpoint_ssd300.pth.tar \
	--extra-files ./trained_models/index_to_name.json,utils.py,model_layers.py \
	--handler object_detector_simple.py \
	--export-path trained_models \
	--requirements-file requirements.txt -f

.PHONY: setup ## setup conda env
setup:
	conda create -n pytorchenv python=3.8 openssl=1.1.1n
	conda install pytorch torchvision torchserve torch-model-archiver -c pytorch
	pip install -r requirements.txt
	conda activate torchenv

.PHONY: serving-status
serving-status:
	curl http://localhost:8080/ping

.PHONY: serving-inference
serving-inference:
	curl -X POST http://localhost:8080/predictions/ols-smart-rack -T example_images_OLS/MicrosoftTeams-image_1.png