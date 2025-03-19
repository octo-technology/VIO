from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, computed_field, model_validator

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
from edge_orchestrator.utils.usb_device import get_camera_device_node


class CameraConfig(BaseModel):
    camera_id: str
    camera_type: CameraType
    source_directory: Optional[Path] = None
    camera_vendor: Optional[str] = None
    camera_serial_number: Optional[str] = None
    same_camera_index: Optional[int] = 0
    position: Optional[str] = "front"
    camera_resolution: Optional[ImageResolution] = None
    model_forwarder_config: Optional[ModelForwarderConfig] = None
    camera_rule_config: Optional[CameraRuleConfig] = None

    @model_validator(mode="after")
    def check_params(self):
        if self.camera_type == CameraType.FAKE and self.source_directory is None:
            raise ValueError("source_directory is required with camera_type FAKE")
        if self.camera_type == CameraType.USB and self.camera_vendor is not None and self.camera_serial_number is None:
            raise ValueError("camera_vendor and camera_serial_number are required with camera_type USB")
        return self

    @computed_field
    @property
    def device_node(self) -> Union[str, int, None]:
        if self.camera_type == CameraType.USB:
            return get_camera_device_node(self.camera_vendor, self.camera_serial_number, self.same_camera_index)
        elif self.camera_type == CameraType.WEBCAM:
            return 0
        else:
            return None
