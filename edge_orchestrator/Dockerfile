FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY pyproject.toml ./pyproject.toml
COPY edge_orchestrator ./edge_orchestrator

RUN apt-get update
RUN apt-get install fswebcam -y
RUN pip install --upgrade pip
RUN pip install .

ENV API_CONFIG docker

EXPOSE 8000
ENTRYPOINT ["python", "-m", "edge_orchestrator"]
