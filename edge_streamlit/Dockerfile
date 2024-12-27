FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .
COPY utils.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py"]
