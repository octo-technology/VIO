import logging
from typing import Dict, List

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_trainer.training_job import TrainingJob
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer import IModelTrainer


class FakeModelTrainer(IModelTrainer):
    """In-memory trainer that reports an immediately-completed fit.

    Lets the trigger/teach flow be exercised end to end without a serving
    backend, exactly as ``FakeModelForwarder`` does for inference.
    """

    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config
        self._jobs: Dict[str, TrainingJob] = {}

    async def add_reference_images(self, binaries: List[bytes]) -> TrainingJob:
        count = len(binaries)
        job = TrainingJob(
            job_id=f"fake-job-{len(self._jobs) + 1}",
            model_name=self._model_forwarder_config.model_name,
            status="completed",
            total=count,
            processed=count,
            bank_size=count,
        )
        self._jobs[job.job_id] = job
        return job

    async def get_training_job(self, job_id: str) -> TrainingJob:
        return self._jobs.get(
            job_id,
            TrainingJob(
                job_id=job_id,
                model_name=self._model_forwarder_config.model_name,
                status="completed",
                total=0,
                processed=0,
                bank_size=0,
            ),
        )
