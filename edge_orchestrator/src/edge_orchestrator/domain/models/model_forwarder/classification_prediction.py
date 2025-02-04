from typing import Literal, Optional

from pydantic import BaseModel

from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)


class ClassifPrediction(BaseModel):
    prediction_type: Literal[PredictionType.class_]
    label: Optional[str] = None
    probability: Optional[float] = None
