ARG PYTHON_VERSION="3.11"

FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /edge_camera

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir uv && uv pip install --system -e "."

EXPOSE 8001
CMD ["uvicorn", "edge_camera.interface.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001"]
