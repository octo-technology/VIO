FROM continuumio/miniconda3:4.12.0
# version freeze due to issue between numpy installation and latest miniconda3 image version

WORKDIR /supervisor

COPY setup.py ./setup.py
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY supervisor ./supervisor
COPY config ./config
COPY data ./data

ENV API_CONFIG docker
CMD python -m supervisor

