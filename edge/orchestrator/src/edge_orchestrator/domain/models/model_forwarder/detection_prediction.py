from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.detected_object import (
    DetectedObject,
)
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)


class DetectionPrediction(BaseModel):
    prediction_type: Literal[PredictionType.objects]
    detected_objects: Dict[str, DetectedObject] = Field(default=dict())
    label: Optional[Decision] = None
