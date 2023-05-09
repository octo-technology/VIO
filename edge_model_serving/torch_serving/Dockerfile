FROM python:3.8-slim

WORKDIR /torch_serving

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./models ./models
COPY ./config.properties ./config.properties
COPY requirements.txt .

# Install OpenJDK
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean;

RUN pip install --upgrade pip
RUN pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
RUN pip install -r requirements.txt

EXPOSE 8080


CMD torchserve --start --model-store ./models --models yolo=yolo5.mar --ts-config ./config.properties --foreground

