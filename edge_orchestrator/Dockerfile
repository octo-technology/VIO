FROM python:3.8.16-slim

ARG GCP_FILE_NAME="acn-gcp-octo-sas-ee685c40af79.json"

WORKDIR /edge_orchestrator

COPY edge_orchestrator ./edge_orchestrator
COPY config ./config
COPY data ./data
COPY setup.py ./setup.py
COPY ${GCP_FILE_NAME} ./${GCP_FILE_NAME}

RUN pip install .

ENV API_CONFIG edge-gcp

ENV GOOGLE_APPLICATION_CREDENTIALS ./${GCP_FILE_NAME}
ENV GCP_BUCKET_NAME=airbus-vio-storage

ENTRYPOINT ["python", "-m", "edge_orchestrator"]

EXPOSE 8000
