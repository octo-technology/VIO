FROM --platform=$TARGETPLATFORM python:3.10-slim AS builder
ARG TARGETPLATFORM

WORKDIR /tflite_serving

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends build-essential gcc
RUN python -m venv /opt/venv
RUN pip install --upgrade pip setuptools

ENV PATH="/opt/venv/bin:$PATH"

COPY tflite_serving/pyproject.toml ./
COPY tflite_serving/src/ ./src

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf; \
        pip install ".[linux]"; \
    else \
        pip install ".[linux]"; \
    fi


FROM --platform=$TARGETPLATFORM python:3.10-slim
ARG TARGETPLATFORM

# RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
#         apt-get update && apt-get install -y fswebcam rpicam-apps-lite; \
#     else \
#         apt-get update && apt-get install -y fswebcam; \
#     fi

RUN apt-get update && apt-get upgrade -y

WORKDIR /tflite_serving

COPY --from=builder /opt/venv /opt/venv
COPY models/tflite/ $MODELS_PATH/tflite/

ENV PATH="/opt/venv/bin:$PATH"
ENV MODELS_PATH=/models

EXPOSE 8501
ENTRYPOINT ["uvicorn", "tflite_serving.tflite_server:app"]
CMD ["--reload", "--port", "8501", "--host", "0.0.0.0" ]
