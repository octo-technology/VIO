ARG PYTHON_VERSION="3.11"

FROM ghcr.io/astral-sh/uv:latest AS uv

# ── builder ───────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

COPY --from=uv /uv /bin/uv

ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libcap-dev \
        libsm6 \
        libxext6 \
        libglib2.0-0 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── runtime ───────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libcap2 \
        libsm6 \
        libxext6 \
        libglib2.0-0 \
        libgl1 \
        ffmpeg \
        v4l-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY fake_images ./fake_images

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001
CMD ["uvicorn", "edge_camera.interface.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001"]
