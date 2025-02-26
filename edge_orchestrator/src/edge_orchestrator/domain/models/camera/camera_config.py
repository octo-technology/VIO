from pathlib import Path
from typing import Optional

from pydantic import BaseModel, model_validator

from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.image_resolution import (
    ImageResolution,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)


class CameraConfig(BaseModel):
    camera_id: str
    camera_type: CameraType
    source_directory: Optional[Path] = None
    position: Optional[str] = "front"
    camera_resolution: Optional[ImageResolution] = None
    model_forwarder_config: Optional[ModelForwarderConfig] = None
    camera_rule_config: Optional[CameraRuleConfig] = None
    recreate_me: Optional[bool] = False

    @model_validator(mode="after")
    def check_params(self):
        if self.camera_type in [CameraType.FAKE, CameraType.USB, CameraType.WEBCAM] and self.source_directory is None:
            raise ValueError("source_directory is required with camera_type FAKE, USB or WEBCAM")
        return self
