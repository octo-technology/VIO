FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder
ARG TARGETPLATFORM

WORKDIR /edge_orchestrator

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc
RUN python -m venv /opt/venv
RUN pip install --upgrade pip setuptools

ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
COPY src/ ./src

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf; \
    pip install ".[raspberry]"; \
    else \
    pip install "."; \
    fi


FROM python:3.12-slim
ARG TARGETPLATFORM

# RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
#         apt-get update && apt-get install -y fswebcam rpicam-apps-lite; \
#     else \
#         apt-get update && apt-get install -y fswebcam; \
#     fi

RUN apt-get update && apt-get install -y fswebcam ffmpeg libsm6 libxext6

WORKDIR /edge_orchestrator

COPY --from=builder /opt/venv /opt/venv
COPY fake_images ./fake_images
COPY model_labels ./model_labels

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000
ENTRYPOINT ["uvicorn", "edge_orchestrator.interface.api.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
