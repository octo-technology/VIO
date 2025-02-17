from typing import Dict, Optional

from pydantic import ConfigDict, Field

from edge_orchestrator.domain.models.binary import Image
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.interface.api.models.item_base import ItemBase


class Item(ItemBase):
    model_config = ConfigDict(use_enum_values=True)

    cameras_metadata: Dict[str, CameraConfig] = Field(default=dict())
    binaries: Dict[str, Image] = Field(default=dict())
    predictions: Dict[str, Prediction] = Field(default=dict())
    camera_decisions: Dict[str, Decision] = Field(default=dict())
    decision: Optional[Decision] = None
    state: ItemState = ItemState.TRIGGER
