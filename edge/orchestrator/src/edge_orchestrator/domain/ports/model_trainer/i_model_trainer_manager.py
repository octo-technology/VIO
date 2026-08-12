from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict, List

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_trainer.training_job import TrainingJob
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer import IModelTrainer
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer_factory import (
    IModelTrainerFactory,
)


class IModelTrainerManager(ABC):
    _model_trainer_factory: IModelTrainerFactory
    _model_trainers: Dict[str, IModelTrainer]
    _logger: Logger

    @abstractmethod
    def _get_model_trainer(self, model_forwarder_config: ModelForwarderConfig) -> IModelTrainer:
        pass

    @abstractmethod
    async def add_reference_images(
        self, station_config: StationConfig, model_name: str, binaries: List[bytes]
    ) -> TrainingJob:
        pass

    @abstractmethod
    async def get_training_job(self, station_config: StationConfig, model_name: str, job_id: str) -> TrainingJob:
        pass

    @abstractmethod
    def reset(self):
        pass
