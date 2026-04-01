import logging
import random

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class FakeModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    async def predict_on_binary(self, binary: bytes) -> Prediction:
        if self._model_forwarder_config.model_type == ModelType.object_detection:
            return DetectionPrediction(
                prediction_type=PredictionType.objects,
                detected_objects={
                    "object_1": DetectedObject(
                        location=[4, 112, 244, 156],
                        objectness=random.uniform(0, 1),
                        label=random.choice(["OK", "KO"]),
                    ),
                    "object_2": DetectedObject(
                        location=[2, 56, 122, 78],
                        objectness=random.uniform(0, 1),
                        label=random.choice(["OK", "KO"]),
                    ),
                },
            )
        return ClassifPrediction(
            prediction_type=PredictionType.class_,
            label=random.choice(["OK", "KO"]),
            probability=random.uniform(0, 1),
        )
