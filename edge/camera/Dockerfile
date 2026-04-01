ARG PYTHON_VERSION="3.11"

FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /edge_camera

COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system -e "."

COPY src/ ./src/

EXPOSE 8001
CMD ["uvicorn", "edge_camera.interface.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001"]
