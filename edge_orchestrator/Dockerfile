FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY setup.py ./setup.py

RUN pip install --upgrade pip
RUN pip install .

COPY edge_orchestrator ./edge_orchestrator

ENV API_CONFIG docker
EXPOSE 8000
ENTRYPOINT ["python", "-m", "edge_orchestrator"]
