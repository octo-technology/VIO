import logging

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class DetectionWithClassifModelForwarder(IModelForwarder):
    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def predict_on_binary(self, binary: bytes) -> Prediction:
        return self._predict(binary)

    def _predict(self, binary_data: bytes) -> Prediction:
        raise NotImplementedError("DetectionWithClassifModelForwarder _predict method not implemented")
