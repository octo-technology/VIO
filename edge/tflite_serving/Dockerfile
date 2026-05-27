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
        patchelf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable \
    && find /app/.venv -name "*.so" -exec patchelf --clear-execstack {} \; 2>/dev/null || true

# ── runtime ───────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY models /models

ENV PATH="/app/.venv/bin:$PATH" \
    MODELS_PATH=/models

EXPOSE 8501
ENTRYPOINT ["uvicorn", "tflite_serving.tflite_server:app"]
CMD ["--port", "8501", "--host", "0.0.0.0"]
