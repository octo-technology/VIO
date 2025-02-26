import logging
from typing import Any, Dict

import numpy as np

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class SegmentationModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def _pre_process_binary(self, binary: bytes) -> np.ndarray:
        raise NotImplementedError("SegmentationModelForwarder _pre_process_binary method not implemented")

    async def _predict(self, preprocessed_binary: np.ndarray) -> Dict[str, Any]:
        raise NotImplementedError("SegmentationModelForwarder _predict method not implemented")

    def _post_process_prediction(self, prediction_response: Dict[str, Any]) -> Prediction:
        raise NotImplementedError("SegmentationModelForwarder _post_process_prediction method not implemented")
