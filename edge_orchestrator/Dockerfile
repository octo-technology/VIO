ARG PYTHON_VERSION="3.11"

FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION}-slim
ARG TARGETPLATFORM
ARG BUILDOS

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ] && [ "$BUILDOS" = "linux" ]; then \
        apt update && apt install -y --no-install-recommends gnupg; \
        echo "deb http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list \
        && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E; \
    fi

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ] && [ "$BUILDOS" = "linux" ]; then \
        apt update && apt install -y \
            python3-pip \
            python3-venv \
            python3-picamera2 \
            gcc \
        && apt clean \
        && apt autoremove \
        && rm -rf /var/cache/apt/archives/* \
        && rm -rf /var/lib/apt/lists/*; \
    else \
        apt update && apt install -y --no-install-recommends \
            build-essential \
            gcc \
            fswebcam \
            ffmpeg \
            libsm6 \
            libxext6 \
        && apt clean \
        && apt autoremove \
        && rm -rf /var/cache/apt/archives/* \
        && rm -rf /var/lib/apt/lists/*; \
    fi

WORKDIR /edge_orchestrator

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ] && [ "$BUILDOS" = "linux" ]; then \
        /usr/bin/python3 -m venv --system-site-packages /opt/venv; \
    else \
        python -m venv /opt/venv; \
    fi

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools

COPY pip.conf /opt/venv/pip.conf
COPY pyproject.toml ./
COPY config ./config
COPY fake_images ./fake_images
COPY model_labels ./model_labels
COPY src/ ./src

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ] && [ "$BUILDOS" = "linux" ]; then \
        pip install --no-cache-dir ".[raspberry]"; \
    else \
        pip install --no-cache-dir "."; \
    fi

EXPOSE 8000
ENTRYPOINT ["uvicorn", "edge_orchestrator.interface.api.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
