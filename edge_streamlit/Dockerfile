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
    # ffmpeg \
    # libsm6 \
    # libxext6 \
    # fswebcam \
    # libpq-dev \
    # libnuma-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8502"]
