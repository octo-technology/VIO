FROM continuumio/miniconda3

WORKDIR /supervisor

COPY setup.py ./setup.py
COPY requirements.txt ./requirements.txt
COPY requirements-dev.txt ./requirements-dev.txt

RUN pip install -r requirements.txt

COPY supervisor ./supervisor
COPY config ./config
COPY data ./data

ENV API_CONFIG docker
CMD python -m supervisor

