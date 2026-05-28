import os
from typing import Optional

from pydantic import BaseModel, Field

from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.model_forwarder.image_resolution import (
    ImageResolution,
)


class CameraConfig(BaseModel):
    camera_id: str
    camera_type: CameraType
    position: str = "front"
    camera_resolution: Optional[ImageResolution] = None
    service_url: str = Field(default_factory=lambda: os.getenv("CAMERA_SERVICE_URL", "http://localhost:8001"))
