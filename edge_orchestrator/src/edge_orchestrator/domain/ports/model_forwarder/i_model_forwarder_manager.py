from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder_factory import (
    IModelForwarderFactory,
)


class IModelForwarderManager(ABC):
    _model_forwarder_factory: IModelForwarderFactory
    _model_forwarders: dict[str, IModelForwarder]
    _logger: Logger

    @abstractmethod
    def _get_model_forwarder(self, model_forwarder_config: ModelForwarderConfig) -> IModelForwarder:
        pass

    @abstractmethod
    def predict_on_binaries(self, item: Item):
        pass

    @abstractmethod
    def reset(self):
        pass
