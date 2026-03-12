import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from edge_camera.domain.models.image_ref import ImageRef

router = APIRouter(tags=["capture"])


def _output_dir(camera_id: str) -> Path:
    base = Path(os.getenv("CAMERA_OUTPUT_DIR", "/dev/shm/vio"))
    return base / camera_id


@router.post("/capture", response_model=ImageRef, summary="Capture a frame from a camera")
async def capture(request: Request, camera_id: Optional[str] = None) -> ImageRef:
    backends = request.app.state.backends

    if camera_id is None:
        if len(backends) != 1:
            raise HTTPException(
                status_code=400,
                detail=f"camera_id is required when multiple cameras are registered: {list(backends.keys())}",
            )
        camera_id = next(iter(backends))

    backend = backends.get(camera_id)
    if backend is None:
        raise HTTPException(status_code=404, detail=f"Camera '{camera_id}' not found")

    return await backend.capture(_output_dir(camera_id), camera_id)


@router.get("/health", summary="Camera service health")
async def health(request: Request) -> dict:
    backends = request.app.state.backends
    return {
        "status": "ok",
        "cameras": {camera_id: backend.health() for camera_id, backend in backends.items()},
    }


@router.get("/metadata", summary="Camera service metadata")
async def metadata(request: Request) -> dict:
    backends = request.app.state.backends
    return {
        "cameras": {camera_id: backend.metadata() for camera_id, backend in backends.items()},
    }
