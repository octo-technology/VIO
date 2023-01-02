FROM continuumio/miniconda3:4.12.0
# version freeze due to issue between numpy installation and latest miniconda3 image version

WORKDIR /edge_orchestrator

COPY setup.py ./setup.py
COPY requirements.txt ./requirements.txt
COPY requirements-dev.txt ./requirements-dev.txt

RUN pip install -e .

COPY edge_orchestrator ./edge_orchestrator
COPY config ./config
COPY data ./data

ENV API_CONFIG docker
CMD python edge_orchestrator

