FROM python:3.8.10-slim

WORKDIR /tflite_serving

COPY tflite_serving/src/ src/
COPY tflite_serving/pyproject.toml .

RUN pip install --upgrade pip
RUN pip install -e ".[linux]"

EXPOSE 8501
CMD [ "uvicorn", "tflite_serving.tflite_server:app", "--reload", "--port", "8501", "--host", "0.0.0.0" ]
