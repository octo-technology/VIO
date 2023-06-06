FROM python:3.8.16-slim

WORKDIR /edge_orchestrator

COPY setup.py ./setup.py

RUN apt-get update
RUN apt-get install fswebcam -y
RUN pip install --upgrade pip
RUN pip install .

COPY edge_orchestrator ./edge_orchestrator

ENV API_CONFIG upload-gcp
ENV SERVING_MODEL_URL http://edge_model_serving:8501
ENV GOOGLE_APPLICATION_CREDENTIALS /edge_orchestrator/config/secrets/credentials.json
ENV GCP_BUCKET_NAME tf-vio-bucket
ENV ACTIVE_CONFIG_NAME barcode_detection_with_usbcamera

EXPOSE 8000
ENTRYPOINT ["python", "-m", "edge_orchestrator"]
