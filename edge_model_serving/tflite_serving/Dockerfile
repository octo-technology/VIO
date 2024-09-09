FROM python:3.8.10-slim

WORKDIR /tflite_serving

RUN apt-get update && apt-get upgrade -y && apt-get install gcc -y
RUN apt-get update && apt-get install -y pkg-config libhdf5-dev

COPY tflite_serving/src/ src/
COPY tflite_serving/pyproject.toml .

RUN pip install --upgrade pip
RUN pip install -e ".[linux]"

ENV MODELS_PATH=/models
COPY models/tflite/ $MODELS_PATH/tflite/

EXPOSE 8501
CMD [ "uvicorn", "tflite_serving.tflite_server:app", "--reload", "--port", "8501", "--host", "0.0.0.0" ]
