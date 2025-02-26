from typing import Literal, Optional

from pydantic import BaseModel, field_validator

from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)


class ClassifPrediction(BaseModel):
    prediction_type: Literal[PredictionType.class_]
    label: Optional[str] = None
    probability: Optional[float] = None

    @field_validator("probability")
    @classmethod
    def round_float(cls, v: float) -> float:
        return round(v, 5)
