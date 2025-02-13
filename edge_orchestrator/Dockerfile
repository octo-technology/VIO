FROM --platform=$TARGETPLATFORM python:3.12-slim AS builder
ARG TARGETPLATFORM

WORKDIR /edge_orchestrator

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools

COPY pyproject.toml ./
COPY src/ ./src
COPY pip.conf /opt/venv/pip.conf

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    pip install ".[raspberry]"; \
    else \
    pip install "."; \
    fi

# Use a conditional statement to select the appropriate base image for the second stage
FROM --platform=$TARGETPLATFORM python:3.12-slim AS base_amd64
FROM --platform=$TARGETPLATFORM bluenviron/mediamtx:latest-rpi AS base_arm64

FROM --platform=$TARGETPLATFORM base_${TARGETPLATFORM##*/} AS final
ARG TARGETPLATFORM

RUN if [ "$TARGETPLATFORM" = "linux/adm64" ]; then \
        apt-get update && apt-get install -y fswebcam; \
    else \
        apt-get update; \
    fi

# RUN apt-get update && apt-get install -y fswebcam ffmpeg libsm6 libxext6

WORKDIR /edge_orchestrator

COPY --from=builder /opt/venv /opt/venv
COPY fake_images ./fake_images
COPY model_labels ./model_labels

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000
ENTRYPOINT ["uvicorn", "edge_orchestrator.interface.api.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
