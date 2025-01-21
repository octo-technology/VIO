from typing import Dict, List, Literal

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType


class DetectedObject(BaseModel):
    location: List[int]
    objectness: float


class DetectionPrediction(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    prediction_type: Literal[ModelType.OBJECT_DETECTION]
    detected_objects: Dict[str, DetectedObject]
