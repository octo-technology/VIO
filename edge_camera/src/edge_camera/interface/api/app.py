import logging
import os
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from edge_camera.domain.ports.i_camera_backend import ICameraBackend
from edge_camera.interface.api.routers.capture import router as capture_router


def _load_backends_from_env() -> Dict[str, ICameraBackend]:
    """Load camera backends from CAMERA_BACKENDS env var.

    Format: "cam_1=fake,cam_2=opencv:0"
      - camera_id=backend_type[:arg]
      - For opencv, the optional arg is the device index (default: 0).
    Defaults to a single fake camera named 'cam_1'.
    """
    from edge_camera.infrastructure.backends.fake_camera_backend import (
        FakeCameraBackend,
    )

    def _make_opencv(arg: str) -> "ICameraBackend":
        from edge_camera.infrastructure.backends.opencv_camera_backend import (
            OpenCvCameraBackend,
        )

        return OpenCvCameraBackend(device_index=int(arg) if arg else 0)

    backend_factories = {
        "fake": lambda arg: FakeCameraBackend(),
        "opencv": _make_opencv,
    }

    spec = os.getenv("CAMERA_BACKENDS", "cam_1=fake")
    backends: Dict[str, ICameraBackend] = {}
    for entry in spec.split(","):
        camera_id, _, backend_spec = entry.strip().partition("=")
        backend_type, _, backend_arg = backend_spec.strip().partition(":")
        factory = backend_factories.get(backend_type.strip())
        if factory is None:
            raise ValueError(f"Unknown camera backend type: '{backend_type}'. Available: {list(backend_factories)}")
        backends[camera_id.strip()] = factory(backend_arg.strip())

    return backends


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Allow tests to pre-populate backends before entering the context manager
    if not hasattr(app.state, "backends"):
        app.state.backends = _load_backends_from_env()
    yield
    app.state.backends = {}


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(asctime)s - %(name)s - %(message)s")
    app = FastAPI(title="edge_camera", lifespan=lifespan)
    app.include_router(capture_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
