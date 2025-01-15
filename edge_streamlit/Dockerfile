FROM python:3.9-slim

# let print debug messages log on the console
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

ENV ORCHESTRATOR_URL=http://edge_orchestrator:8000/api/v1/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .
COPY utils.py .
COPY prediction_boxes.py .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py"]
