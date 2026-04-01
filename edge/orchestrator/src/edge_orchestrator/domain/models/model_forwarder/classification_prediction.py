from typing import Annotated, Literal, Optional

from pydantic import AfterValidator, BaseModel

from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.models.validators import round_float


class ClassifPrediction(BaseModel):
    prediction_type: Literal[PredictionType.class_]
    label: Optional[str] = None
    probability: Annotated[Optional[float], AfterValidator(round_float)] = None
