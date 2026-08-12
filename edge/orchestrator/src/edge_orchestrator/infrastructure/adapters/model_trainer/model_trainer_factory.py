import logging

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer import IModelTrainer
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer_factory import (
    IModelTrainerFactory,
)


class ModelTrainerFactory(IModelTrainerFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_model_trainer(self, model_forwarder_config: ModelForwarderConfig) -> IModelTrainer:
        if model_forwarder_config.model_name == "fake_model":
            from edge_orchestrator.infrastructure.adapters.model_trainer.fake_model_trainer import (
                FakeModelTrainer,
            )

            return FakeModelTrainer(model_forwarder_config)

        from edge_orchestrator.infrastructure.adapters.model_trainer.model_trainer import (
            ModelTrainer,
        )

        return ModelTrainer(model_forwarder_config)
