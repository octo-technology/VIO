import logging
from typing import Dict, List, Optional

from edge_orchestrator.domain.exceptions import ModelNotInConfigError
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_trainer.training_job import TrainingJob
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer import IModelTrainer
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer_factory import (
    IModelTrainerFactory,
)
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer_manager import (
    IModelTrainerManager,
)


class ModelTrainerManager(IModelTrainerManager):
    def __init__(self, model_trainer_factory: IModelTrainerFactory):
        self._model_trainer_factory = model_trainer_factory
        self._model_trainers: Dict[str, IModelTrainer] = {}
        self._logger = logging.getLogger(__name__)

    def _get_model_trainer(self, model_forwarder_config: ModelForwarderConfig) -> IModelTrainer:
        model_id = model_forwarder_config.model_id
        if model_id not in self._model_trainers:
            self._logger.info(f"Creating model trainer for model_id: {model_id}")
            self._model_trainers[model_id] = self._model_trainer_factory.create_model_trainer(model_forwarder_config)
        return self._model_trainers[model_id]

    @staticmethod
    def _resolve_config(station_config: StationConfig, model_name: str) -> Optional[ModelForwarderConfig]:
        for step in station_config.pipeline_steps.values():
            if step.model_forwarder_config.model_name == model_name:
                return step.model_forwarder_config
        return None

    def _trainer_for(self, station_config: StationConfig, model_name: str) -> IModelTrainer:
        config = self._resolve_config(station_config, model_name)
        if config is None:
            raise ModelNotInConfigError(f"Model '{model_name}' is not used by the active configuration")
        return self._get_model_trainer(config)

    async def add_reference_images(
        self, station_config: StationConfig, model_name: str, binaries: List[bytes]
    ) -> TrainingJob:
        return await self._trainer_for(station_config, model_name).add_reference_images(binaries)

    async def get_training_job(self, station_config: StationConfig, model_name: str, job_id: str) -> TrainingJob:
        return await self._trainer_for(station_config, model_name).get_training_job(job_id)

    def reset(self):
        self._model_trainers = {}
