FROM python:3.7

WORKDIR /tflite_serving

COPY requirements.txt .
RUN pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_x86_64.whl
RUN pip install -r requirements.txt

COPY tflite_serving/tflite_server.py .
COPY models ./models

ENV TPU false
EXPOSE 8501
CMD [ "uvicorn", "tflite_server:app", "--reload", "--port", "8501", "--host", "0.0.0.0" ]
