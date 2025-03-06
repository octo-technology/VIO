FROM pytorch/torchserve:0.12.0-cpu

WORKDIR /torch_serving

COPY torch_serving/requirements.txt .
COPY torch_serving/model.py model.py
COPY models/torch ./models

USER root
RUN apt-get update \
	&& apt-get install -y wget \
	&& apt clean;
RUN wget -o ./models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth  https://download.pytorch.org/models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth
RUN chown -R model-server:model-server /torch_serving
USER model-server

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN torch-model-archiver \
	--model-name fastrcnn \
	--version 1.0 \
	--model-file model.py \
	--serialized-file ./models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth \
	--handler object_detector \
	--extra-files ./models/index_to_name.json -f

CMD ["torchserve", "--start", "--model-store", "./models", "--models", "fastrcnn=fastrcnn.mar"]
