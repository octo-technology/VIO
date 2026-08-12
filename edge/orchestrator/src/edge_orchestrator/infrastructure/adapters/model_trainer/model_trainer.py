import logging
from typing import List

import aiohttp

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_trainer.training_job import TrainingJob
from edge_orchestrator.domain.ports.model_trainer.i_model_trainer import IModelTrainer


class ModelTrainer(IModelTrainer):
    """Forwards reference images to a serving backend and polls the fit job.

    The orchestrator does none of the fitting itself: it streams the uploaded
    normal images to the model server's ``reference-images`` endpoint and relays
    the job it returns. Progress is read back from the same server.
    """

    def __init__(self, model_forwarder_config: ModelForwarderConfig):
        self._logger = logging.getLogger(__name__)
        self._model_forwarder_config = model_forwarder_config

    def _base_url(self) -> str:
        url = self._model_forwarder_config.model_serving_url
        if url is None:
            raise ValueError(f"No model_serving_url set for model '{self._model_forwarder_config.model_name}'")
        return str(url).rstrip("/")

    def _reference_images_url(self) -> str:
        return f"{self._base_url()}/v1/models/{self._model_forwarder_config.model_name}/reference-images"

    async def add_reference_images(self, binaries: List[bytes]) -> TrainingJob:
        form = aiohttp.FormData()
        for index, binary in enumerate(binaries):
            form.add_field(
                "files",
                binary,
                filename=f"reference_{index}.jpg",
                content_type="application/octet-stream",
            )
        self._logger.info(f"Submitting {len(binaries)} reference image(s) to {self._reference_images_url()}")
        async with aiohttp.ClientSession() as session:
            async with session.post(self._reference_images_url(), data=form) as response:
                response.raise_for_status()
                body = await response.json(content_type=None)
        return TrainingJob(
            job_id=body["job_id"],
            model_name=self._model_forwarder_config.model_name,
            status=body["status"],
            total=body["total"],
        )

    async def get_training_job(self, job_id: str) -> TrainingJob:
        url = f"{self._reference_images_url()}/jobs/{job_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                body = await response.json(content_type=None)
        return TrainingJob(**body)
