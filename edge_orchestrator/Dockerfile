FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY edge_orchestrator ./edge_orchestrator
COPY config ./config
COPY data ./data
COPY setup.py ./setup.py
COPY acn-gcp-octo-sas-dcf57c073399.json ./acn-gcp-octo-sas-dcf57c073399.json

RUN pip install .

ENV API_CONFIG docker

ENV API_CONFIG test-gcp
ENV GOOGLE_APPLICATION_CREDENTIALS ./acn-gcp-octo-sas-dcf57c073399.json

ENTRYPOINT ["python", "-m", "edge_orchestrator"]

EXPOSE 8000
