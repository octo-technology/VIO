from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)


class IModelForwarder(ABC):
    _logger: Logger
    _model_forwarder_config: ModelForwarderConfig

    @abstractmethod
    def predict_on_binary(self, binary: bytes):
        pass
