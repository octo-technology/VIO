import logging
import random

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectedObject,
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.detection_prediction_with_classif import (
    DetectedObjectWithClassif,
    DetectionPredictionWithClassif,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class FakeModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def predict_on_binary(self, binary: bytes) -> Prediction:
        return self._predict(binary)

    def _predict(self, binary_data: bytes) -> Prediction:
        model_type = self._model_forwarder_config.model_type
        if model_type == ModelType.CLASSIFICATION.value or model_type == ModelType.FAKE.value:
            return ClassifPrediction(
                prediction_type=ModelType.CLASSIFICATION,
                label=random.choice([Decision.OK, Decision.KO]),
                probability=random.uniform(0, 1),
            )
        elif model_type == ModelType.OBJECT_DETECTION.value:
            return DetectionPrediction(
                prediction_type=ModelType.CLASSIFICATION,
                detected_objects={
                    "object_1": DetectedObject(location=[4, 112, 244, 156], objectness=random.uniform(0, 1)),
                    "object_2": DetectedObject(location=[2, 56, 122, 78], objectness=random.uniform(0, 1)),
                },
            )
        elif model_type == ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION.value:
            return DetectionPredictionWithClassif(
                prediction_type=ModelType.CLASSIFICATION,
                detected_objects={
                    "object_1": DetectedObjectWithClassif(
                        label=random.choice([Decision.OK, Decision.KO]),
                        probability=random.uniform(0, 1),
                        location=[4, 112, 244, 156],
                        objectness=random.uniform(0, 1),
                    ),
                    "object_2": DetectedObjectWithClassif(
                        label=random.choice([Decision.OK, Decision.KO]),
                        probability=random.uniform(0, 1),
                        location=[2, 56, 122, 78],
                        objectness=random.uniform(0, 1),
                    ),
                },
            )
