FROM python:3.8-alpine

WORKDIR /supervisor

COPY setup.py ./setup.py
COPY requirements.txt ./requirements.txt
COPY requirements-dev.txt ./requirements-dev.txt

RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev zlib-dev libjpeg-turbo-dev libffi-dev
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY supervisor ./supervisor
COPY config ./config
COPY data ./data

ENV API_CONFIG docker
CMD python -m supervisor

