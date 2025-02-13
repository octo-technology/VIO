FROM --platform=$TARGETPLATFORM python:3.10-slim AS builder
ARG TARGETPLATFORM
ARG BUILDOS

WORKDIR /tflite_serving

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && apt clean \
    && apt autoremove \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools


COPY tflite_serving/pyproject.toml ./
COPY tflite_serving/src/ ./src
COPY tflite_serving/pip.conf /opt/venv/pip.conf
COPY models/tflite/ $MODELS_PATH/tflite/

RUN pip install --no-cache-dir ".[linux]"

ENV MODELS_PATH=/models

EXPOSE 8501
ENTRYPOINT ["uvicorn", "tflite_serving.tflite_server:app"]
CMD ["--reload", "--port", "8501", "--host", "0.0.0.0" ]
