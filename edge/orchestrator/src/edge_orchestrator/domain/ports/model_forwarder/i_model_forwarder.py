from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.prediction import Prediction


class IModelForwarder(ABC):
    _logger: Logger
    _model_forwarder_config: ModelForwarderConfig

    @abstractmethod
    async def predict_on_binary(self, binary: bytes) -> Prediction:
        pass

    @staticmethod
    def _build_model_url(base_url: str, model_name: str, model_version: str) -> str:
        if base_url.endswith("/"):
            return f"{base_url}v1/models/{model_name}/versions/{model_version}:predict"
        else:
            return f"{base_url}/v1/models/{model_name}/versions/{model_version}:predict"

    def _get_model_url(self) -> str:
        return self._build_model_url(
            str(self._model_forwarder_config.model_serving_url),
            self._model_forwarder_config.model_name,
            self._model_forwarder_config.model_version,
        )
