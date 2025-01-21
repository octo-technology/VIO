from typing import Literal

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType


class ClassifPrediction(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    prediction_type: Literal[ModelType.CLASSIFICATION]
    label: Decision
    probability: float
