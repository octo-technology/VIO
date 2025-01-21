from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.item_rule.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)


class CameraConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    camera_id: str
    camera_type: CameraType
    source_directory: Optional[Path] = None
    position: Optional[str] = "front"
    model_forwarder_config: Optional[ModelForwarderConfig] = None
    camera_rule_config: Optional[CameraRuleConfig] = None
