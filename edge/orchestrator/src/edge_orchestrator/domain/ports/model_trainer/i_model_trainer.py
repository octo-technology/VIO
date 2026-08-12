from abc import ABC, abstractmethod
from logging import Logger
from typing import List

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_trainer.training_job import TrainingJob


class IModelTrainer(ABC):
    """Teaches a serving-side model new anomaly-free reference images.

    A model is identified by the same ``ModelForwarderConfig`` a pipeline step
    uses (serving URL, name, version) — training and inference target the very
    same model, so they share its coordinates.
    """

    _logger: Logger
    _model_forwarder_config: ModelForwarderConfig

    @abstractmethod
    async def add_reference_images(self, binaries: List[bytes]) -> TrainingJob:
        """Submit normal images to extend the model's memory bank; returns the job."""

    @abstractmethod
    async def get_training_job(self, job_id: str) -> TrainingJob:
        """Fetch the current progress of a previously submitted fit job."""
