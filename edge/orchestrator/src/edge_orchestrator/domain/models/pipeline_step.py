from typing import Optional

from pydantic import BaseModel

from edge_orchestrator.domain.models.camera_rule.camera_rule_config import (
    CameraRuleConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)


class PipelineStep(BaseModel):
    camera_id: str
    model_forwarder_config: ModelForwarderConfig
    camera_rule_config: Optional[CameraRuleConfig] = None
