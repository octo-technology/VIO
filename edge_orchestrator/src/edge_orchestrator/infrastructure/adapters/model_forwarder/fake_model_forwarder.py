import logging
import random
from typing import Any, Dict

import numpy as np

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
        return await super().predict_on_binary(binary)

    def _pre_process_binary(self, binary: bytes) -> np.ndarray:
        width = self._model_forwarder_config.image_resolution.width
        height = self._model_forwarder_config.image_resolution.height
        return np.ndarray(shape=(1, width, height, 3), dtype=np.float32, buffer=np.random.rand(1, width, height, 3))

    async def _predict(self, preprocessed_binary: np.ndarray) -> Dict[str, Any]:
        model_type = self._model_forwarder_config.model_type
        # TODO: remove ModelType.FAKE
        if model_type == ModelType.classification or model_type == ModelType.FAKE:
            return {"label": random.choice(["OK", "KO"]), "probability": random.uniform(0, 1)}
        elif model_type == ModelType.object_detection:
            return {
                "detected_objects": {
                    "object_1": {
                        "label": random.choice(["OK", "KO"]),
                        "location": [4, 112, 244, 156],
                        "objectness": random.uniform(0, 1),
                    },
                    "object_2": {
                        "label": random.choice(["OK", "KO"]),
                        "location": [2, 56, 122, 78],
                        "objectness": random.uniform(0, 1),
                    },
                },
            }

    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        model_type = self._model_forwarder_config.model_type
        if model_type == ModelType.classification.value or model_type == ModelType.FAKE.value:
            return ClassifPrediction(
                prediction_type=PredictionType.class_,
                label=prediction_response["label"],
                probability=prediction_response["probability"],
            )
        elif model_type == ModelType.object_detection.value:
            detected_objects = prediction_response["detected_objects"]
            return DetectionPrediction(
                prediction_type=PredictionType.objects,
                detected_objects={
                    "object_1": DetectedObject(
                        prediction_type=ModelType.classification,
                        label=detected_objects["object_1"]["label"],
                        location=detected_objects["object_1"]["location"],
                        objectness=detected_objects["object_1"]["objectness"],
                    ),
                    "object_2": DetectedObject(
                        prediction_type=ModelType.classification,
                        label=detected_objects["object_2"]["label"],
                        location=detected_objects["object_2"]["location"],
                        objectness=detected_objects["object_2"]["objectness"],
                    ),
                },
            )
