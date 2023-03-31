FROM python:3.7

WORKDIR /torch_serving

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN download-models
RUN build-mar-file

COPY ../models/torch ./models

RUN torchserve --start --model-store ../models --models fastrcnn=fastrcnn.mar
