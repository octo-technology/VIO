from datetime import datetime
from typing import Dict, Optional

from pydantic import ConfigDict, Field

from edge_orchestrator.domain.models.binary import Image
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item_state import ItemState
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.interface.api.models.item_base import ItemBase


# TODO: add a state or "all steps" that the item passed
class Item(ItemBase):
    model_config = ConfigDict(use_enum_values=True)

    creation_date: datetime = Field(default_factory=datetime.now)
    cameras_metadata: Dict[str, CameraConfig] = Field(default_factory=dict)
    binaries: Dict[str, Image] = Field(default_factory=dict)
    predictions: Dict[str, Prediction] = Field(default_factory=dict)
    camera_decisions: Dict[str, Decision] = Field(default_factory=dict)
    decision: Optional[Decision] = None
    state: ItemState = ItemState.TRIGGER
