FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY pyproject.toml ./pyproject.toml
COPY edge_orchestrator ./edge_orchestrator

RUN apt-get update -y
RUN apt-get install fswebcam -y
RUN apt-get install libpq-dev zlib1g-dev jq gcc libnuma-dev -y
RUN pip install --upgrade pip
RUN pip install .
RUN pip install psycopg2==2.9.3

ENV API_CONFIG docker

EXPOSE 8000
ENTRYPOINT ["python", "-m", "edge_orchestrator"]
