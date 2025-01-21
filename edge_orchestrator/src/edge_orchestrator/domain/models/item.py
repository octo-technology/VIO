from typing import Dict, Optional

from pydantic import ConfigDict, Field

from edge_orchestrator.application.models.item_base import ItemBase
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction


class Item(ItemBase):
    model_config = ConfigDict(use_enum_values=True)

    cameras_metadata: Dict[str, CameraConfig] = Field(default_factory=dict)
    binaries: Dict[str, bytes] = Field(default_factory=dict)
    predictions: Dict[str, Prediction] = Field(default_factory=dict)
    camera_decisions: Dict[str, Decision] = Field(default_factory=dict)
    decision: Optional[Decision] = None
