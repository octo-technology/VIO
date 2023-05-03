FROM python:3.7

WORKDIR /torch_serving

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src .

EXPOSE 8501
CMD [ "uvicorn", "fast_serving:app", "--reload", "--port", "8501", "--host", "0.0.0.0" ]
