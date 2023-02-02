FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY edge_orchestrator ./edge_orchestrator
COPY config ./config
COPY data ./data
COPY setup.py ./setup.py

ENV PIP_INDEX_URL="https://artifactory.michelin.com/api/pypi/pypi/simple"
# Say pip to use artifactory
RUN pip install --upgrade pip
RUN pip install .

ENV API_CONFIG docker

ENTRYPOINT ["python", "-m", "edge_orchestrator"]

EXPOSE 8000
