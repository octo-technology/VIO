import logging

import aiohttp

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
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.models.model_forwarder.prediction_type import (
    PredictionType,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class ModelForwarder(IModelForwarder):
    """Unified model forwarder — sends raw image bytes, receives structured prediction.

    All model-specific logic (preprocessing, postprocessing, class name mapping)
    is handled by the serving layer, driven by its metadata.json.
    """

    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    async def predict_on_binary(self, binary: bytes) -> Prediction:
        self._logger.info(f"Forwarding binary to: {self._get_model_url()}")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._get_model_url(),
                data=binary,
                headers={"Content-Type": "application/octet-stream"},
            ) as response:
                result = await response.json()

        return self._parse_prediction(result)

    def _parse_prediction(self, result: dict) -> Prediction:
        prediction_type = result.get("prediction_type")
        if prediction_type == PredictionType.class_:
            return ClassifPrediction(
                prediction_type=PredictionType.class_,
                label=result.get("label"),
                probability=result.get("probability"),
            )
        elif prediction_type == PredictionType.objects:
            detected_objects = {
                key: DetectedObject(
                    location=obj["location"],
                    objectness=obj["objectness"],
                    label=obj.get("label"),
                )
                for key, obj in result.get("detected_objects", {}).items()
            }
            return DetectionPrediction(
                prediction_type=PredictionType.objects,
                detected_objects=detected_objects,
            )
        else:
            raise ValueError(f"Unknown prediction_type '{prediction_type}' in serving response")
