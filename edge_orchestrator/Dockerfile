FROM python:3.12-slim

WORKDIR /edge_ai

COPY pyproject.toml pyproject.toml
COPY src ./src

RUN apt-get update -y
RUN apt-get install fswebcam -y
# to avoid error "psycopg2.OperationalError: SCRAM authentication requires libpq version 10 or above"
RUN apt-get install libpq-dev zlib1g-dev jq gcc libnuma-dev -y
RUN pip install --upgrade pip setuptools
RUN pip install .

EXPOSE 8000
ENTRYPOINT ["uvicorn", "edge_orchestrator:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
