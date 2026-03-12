import asyncio
import contextlib
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List

import httpx
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend
from edge_camera.interface.api._paths import output_dir as _output_dir
from edge_camera.interface.api.routers.capture import router as capture_router

logger = logging.getLogger(__name__)


async def _run_push_task(backend: ICameraBackend, camera_id: str, push_url: str, out_dir: Path) -> None:
    """Continuously capture frames from a backend and POST each ImageRef to push_url."""
    async with httpx.AsyncClient() as client:

        async def on_frame(ref: ImageRef) -> None:
            try:
                await client.post(push_url, json=ref.model_dump(mode="json"), timeout=5.0)
            except Exception as exc:
                logger.warning("Push failed for camera %s: %s", camera_id, exc)

        await backend.start_listening(out_dir, camera_id, on_frame)


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

    def _make_picamera2(arg: str) -> "ICameraBackend":
        from edge_camera.infrastructure.backends.picamera2_backend import (
            Picamera2Backend,
        )

        return Picamera2Backend(camera_num=int(arg) if arg else 0)

    def _make_basler(arg: str) -> "ICameraBackend":
        from edge_camera.infrastructure.backends.basler_camera_backend import (
            BaslerCameraBackend,
        )

        return BaslerCameraBackend(serial_number=arg if arg else None)

    backend_factories = {
        "fake": lambda arg: FakeCameraBackend(),
        "opencv": _make_opencv,
        "picamera2": _make_picamera2,
        "basler": _make_basler,
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
    if not hasattr(app.state, "backends"):
        app.state.backends = _load_backends_from_env()

    push_url = os.getenv("CAMERA_PUSH_URL", "")
    push_tasks: List[asyncio.Task] = []
    if push_url:
        for camera_id, backend in app.state.backends.items():
            task = asyncio.create_task(_run_push_task(backend, camera_id, push_url, _output_dir(camera_id)))
            push_tasks.append(task)
            logger.info("Push mode: camera %s → %s", camera_id, push_url)

    yield

    for task in push_tasks:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
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
