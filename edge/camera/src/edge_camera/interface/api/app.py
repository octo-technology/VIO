import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List

import httpx
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from edge_camera.domain.models.image_ref import ImageRef
from edge_camera.domain.ports.i_camera_backend import ICameraBackend
from edge_camera.interface.api._paths import output_dir as _output_dir
from edge_camera.interface.api.config import CameraBackendConfig, CameraServiceConfig
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


def _build_backend(camera_id: str, cfg: CameraBackendConfig) -> ICameraBackend:
    backend_type = cfg.backend

    if backend_type == "fake":
        from edge_camera.infrastructure.backends.fake_camera_backend import (
            FakeCameraBackend,
        )

        return FakeCameraBackend()

    if backend_type == "opencv":
        from edge_camera.infrastructure.backends.opencv_camera_backend import (
            OpenCvCameraBackend,
        )

        return OpenCvCameraBackend(device_index=cfg.device_index)

    if backend_type == "picamera2":
        from edge_camera.infrastructure.backends.picamera2_backend import (
            Picamera2Backend,
        )

        return Picamera2Backend(camera_num=cfg.camera_num)

    if backend_type == "basler":
        from edge_camera.infrastructure.backends.basler_camera_backend import (
            BaslerCameraBackend,
        )

        return BaslerCameraBackend(serial_number=cfg.serial_number)

    raise ValueError(f"Unknown camera backend type: '{backend_type}'. Available: fake, opencv, picamera2, basler")


def _build_backends(service_config: CameraServiceConfig) -> Dict[str, ICameraBackend]:
    return {camera_id: _build_backend(camera_id, cfg) for camera_id, cfg in service_config.cameras.items()}


@asynccontextmanager
async def lifespan(app: FastAPI):
    service_config = CameraServiceConfig.load()

    if not hasattr(app.state, "backends"):
        app.state.backends = _build_backends(service_config)

    push_tasks: List[asyncio.Task] = []
    if service_config.push_url:
        for camera_id, backend in app.state.backends.items():
            out_dir = (
                Path(service_config.output_dir) / camera_id if service_config.output_dir else _output_dir(camera_id)
            )
            task = asyncio.create_task(_run_push_task(backend, camera_id, service_config.push_url, out_dir))
            push_tasks.append(task)
            logger.info("Push mode: camera %s → %s", camera_id, service_config.push_url)

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
