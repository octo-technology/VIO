from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from edge_orchestrator.domain.models.item_rule.camera_rule.camera_rule_type import (
    CameraRuleType,
)


class CameraRuleConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    camera_rule_type: CameraRuleType
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
