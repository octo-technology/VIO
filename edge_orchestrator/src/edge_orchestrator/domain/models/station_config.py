from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig


class StationConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    station_name: str
    camera_configs: Dict[str, CameraConfig]
    binary_storage_config: StorageConfig
    metadata_storage_config: StorageConfig
    item_rule_config: Optional[ItemRuleConfig] = None
