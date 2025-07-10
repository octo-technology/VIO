FROM python:3.8-slim

WORKDIR /app  

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install gcc -y


COPY src /app/src
COPY pyproject.toml /app/
COPY models/onnx /models/onnx


# dependances
RUN pip install --upgrade pip 
RUN pip install -e "/app[linux]"


EXPOSE 8000

CMD ["sh", "-c", "PYTHONPATH=/app/src uvicorn onnx_server:app --reload --host 0.0.0.0 --port 8000"]
