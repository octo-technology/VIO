from typing import Annotated, Union

from pydantic import Field

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectionPrediction,
)

Prediction = Annotated[
    Union[ClassifPrediction, DetectionPrediction],
    Field(discriminator="prediction_type"),
]
