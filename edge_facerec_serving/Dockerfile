FROM python:3.7

WORKDIR /edge_facerec_serving

RUN apt-get update
RUN apt install -y libprotobuf-dev protobuf-compiler
RUN apt-get -y install cmake

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY facerec_serving/facerec_server.py .
COPY allowed_photos ./allowed_photos

ENV TPU false
EXPOSE 8501
CMD [ "uvicorn", "facerec_server:app", "--reload", "--port", "8501", "--host", "0.0.0.0" ]
