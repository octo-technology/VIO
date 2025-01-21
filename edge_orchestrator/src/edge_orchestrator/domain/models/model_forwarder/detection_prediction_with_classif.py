from typing import Dict, Literal

from pydantic import BaseModel, ConfigDict

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
)
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType


class DetectedObjectWithClassif(DetectedObject, ClassifPrediction):
    pass


class DetectionPredictionWithClassif(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    prediction_type: Literal[ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION]
    detected_objects: Dict[str, DetectedObjectWithClassif]
