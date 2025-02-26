import io
import logging
from typing import Any, Dict

import aiohttp
import numpy as np
from PIL import Image, ImageOps

from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
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


class ClassifModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def _pre_process_binary(self, binary: bytes) -> np.ndarray:
        width = self._model_forwarder_config.expected_image_resolution.width
        height = self._model_forwarder_config.expected_image_resolution.height
        resized_image = ImageOps.fit(Image.open(io.BytesIO(binary)), (width, height), Image.Resampling.LANCZOS)
        image_array = np.asarray(resized_image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        return np.ndarray(shape=(1, width, height, 3), dtype=np.float32, buffer=normalized_image_array)

    async def _predict(self, preprocessed_binary: np.ndarray) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self._get_model_url(), json={"inputs": preprocessed_binary.tolist()}) as response:
                return await response.json()

    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        if len(prediction_response["outputs"]) == 0:
            self._logger.warning("No predictions found")
            return ClassifPrediction(prediction_type=PredictionType.class_)

        predictions = prediction_response["outputs"][0]
        number_predictions_classes = len(predictions)
        class_names = self._get_class_names()
        number_model_classes = len(class_names)
        if number_predictions_classes != number_model_classes:
            self._logger.warning(
                f"Number of classes in the model ({number_model_classes}) is different from"
                "the number of predictions ({number_predictions_classes})"
            )
        return ClassifPrediction(
            prediction_type=PredictionType.class_,
            label=class_names[np.argmax(predictions)],
            probability=float(np.max(predictions)),
        )
