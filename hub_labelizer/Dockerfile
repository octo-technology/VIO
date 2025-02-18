FROM python:3.10-slim

WORKDIR /hub_labelizer

COPY pyproject.toml ./pyproject.toml
COPY hub_labelizer ./hub_labelizer

RUN apt-get update -y
# to avoid error "psycopg2.OperationalError: SCRAM authentication requires libpq version 10 or above"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install libpq-dev zlib1g-dev jq gcc libnuma-dev -y
RUN pip install --upgrade pip
RUN pip install .
RUN pip install opencv-python

ENV API_CONFIG docker

EXPOSE 8000
ENTRYPOINT ["python", "-m", "hub_labelizer"]
