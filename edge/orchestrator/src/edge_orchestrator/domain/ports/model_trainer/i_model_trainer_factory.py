from abc import ABC, abstractmethod
from logging import Logger

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer import IModelTrainer


class IModelTrainerFactory(ABC):
    _logger: Logger

    @abstractmethod
    def create_model_trainer(self, model_forwarder_config: ModelForwarderConfig) -> IModelTrainer:
        pass
