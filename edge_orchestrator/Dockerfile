FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY setup.py ./setup.py

# ENV PIP_INDEX_URL="https://artifactory.michelin.com/api/pypi/pypi/simple"

RUN pip install --upgrade pip
RUN pip install .

COPY edge_orchestrator ./edge_orchestrator

ENV API_CONFIG docker

ENTRYPOINT ["python", "-m", "edge_orchestrator"]

EXPOSE 8000
