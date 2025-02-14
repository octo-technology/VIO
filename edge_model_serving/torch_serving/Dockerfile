FROM python:3.12

WORKDIR /torch_serving

COPY torch_serving/requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY models/torch ./models/torch

COPY torch_serving/model.py .

COPY torch_serving/Makefile .
RUN make download-models
RUN make build-mar-file

RUN torchserve --start --model-store models --models fastrcnn=fastrcnn.mar
