from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)


class IModelForwarderFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_model_forwarder(self, model_forwarder_config: ModelForwarderConfig) -> IModelForwarder:
        pass
