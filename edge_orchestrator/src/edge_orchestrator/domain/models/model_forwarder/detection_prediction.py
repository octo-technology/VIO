from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)


class DetectedObject(BaseModel):
    location: List[float] = Field(..., min_length=4, max_length=4)
    objectness: float
    label: Optional[str] = None


class DetectionPrediction(BaseModel):
    prediction_type: Literal[PredictionType.objects]
    detected_objects: Dict[str, DetectedObject]
    label: Optional[Decision] = None
