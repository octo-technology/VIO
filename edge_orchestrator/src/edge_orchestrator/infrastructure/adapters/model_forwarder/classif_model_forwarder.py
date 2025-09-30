import logging
from typing import Any, Dict

import numpy as np
from aiohttp import ClientSession, FormData

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

    def _pre_process_binary(self, binary: bytes) -> bytes:
        # Return the original binary data for form upload
        return binary

    async def _predict(self, preprocessed_binary: bytes) -> Dict[str, Any]:
        headers = {}
        if self._model_forwarder_config.domain_name:
            headers["Host"] = self._model_forwarder_config.domain_name

        data = FormData()
        data.add_field("file", preprocessed_binary, filename="image.jpg", content_type="image/jpeg")

        async with ClientSession() as session:
            async with session.post(self._get_model_url(), data=data, headers=headers) as response:
                self._logger.info(f"Response status: {response.status}")
                if response.status != 200:
                    response_text = await response.text()
                    self._logger.error(f"Error response: {response_text}")
                    raise Exception(f"HTTP {response.status}: {response_text}")
                return await response.json()

    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        if len(prediction_response["outputs"]) == 0:
            self._logger.warning("No predictions found")
            return ClassifPrediction(prediction_type=PredictionType.class_)

        self._logger.info(f"Prediction response: {prediction_response}")
        self._logger.info(f"Prediction response outputs: {prediction_response['outputs']}")
        predictions = prediction_response["outputs"]
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
