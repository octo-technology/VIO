from typing import Literal, Optional

from pydantic import BaseModel

from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)


class ClassifPrediction(BaseModel):
    # TODO: see the impact of this line in other BaseModel classes
    # model_config = ConfigDict(use_enum_values=True)

    prediction_type: Literal[PredictionType.class_]
    label: Optional[str] = None
    probability: Optional[float] = None
