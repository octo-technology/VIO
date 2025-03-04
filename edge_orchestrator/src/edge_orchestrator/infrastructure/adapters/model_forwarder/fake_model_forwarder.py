import logging
from typing import Any, Dict

import numpy as np

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


class FakeModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def _pre_process_binary(self, binary: bytes) -> np.ndarray:
        return np.ndarray(shape=(1, 224, 224, 3), dtype=np.float16)

    async def _predict(self, preprocessed_binary: np.ndarray) -> Dict[str, Any]:
        return {"label": "KO", "probability": 0.9999}

    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        return ClassifPrediction(
            prediction_type=PredictionType.class_,
            label=prediction_response["label"],
            probability=prediction_response["probability"],
        )
