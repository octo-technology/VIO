import pytest

from edge_orchestrator.domain.exceptions import ModelNotInConfigError
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.pipeline_step import PipelineStep
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.infrastructure.adapters.model_trainer.model_trainer_factory import (
    ModelTrainerFactory,
)
from edge_orchestrator.infrastructure.adapters.model_trainer.model_trainer_manager import (
    ModelTrainerManager,
)


def _station_config(model_name: str = "fake_model") -> StationConfig:
    return StationConfig(
        station_name="test_station",
        camera_configs={},
        pipeline_steps={
            "step_1": PipelineStep(
                camera_id="camera_1",
                model_forwarder_config=ModelForwarderConfig(model_name=model_name, model_version="1"),
            )
        },
        binary_storage_config=StorageConfig(),
        metadata_storage_config=StorageConfig(),
    )


class TestModelTrainerManager:
    async def test_add_reference_images_forwards_to_the_resolved_trainer(self):
        manager = ModelTrainerManager(ModelTrainerFactory())

        job = await manager.add_reference_images(_station_config(), "fake_model", [b"a", b"b"])

        assert job.model_name == "fake_model"
        assert job.status == "completed"
        assert job.total == 2

    async def test_get_training_job_reuses_the_cached_trainer(self):
        manager = ModelTrainerManager(ModelTrainerFactory())
        station_config = _station_config()
        submitted = await manager.add_reference_images(station_config, "fake_model", [b"a"])

        fetched = await manager.get_training_job(station_config, "fake_model", submitted.job_id)

        assert fetched == submitted

    async def test_raises_when_the_model_is_not_in_the_active_config(self):
        manager = ModelTrainerManager(ModelTrainerFactory())

        with pytest.raises(ModelNotInConfigError):
            await manager.add_reference_images(_station_config(), "not_configured", [b"a"])

    async def test_caches_one_trainer_per_model_id(self):
        manager = ModelTrainerManager(ModelTrainerFactory())
        config = ModelForwarderConfig(model_name="fake_model", model_version="1")

        first = manager._get_model_trainer(config)
        second = manager._get_model_trainer(config)

        assert first is second

    async def test_reset_drops_cached_trainers(self):
        manager = ModelTrainerManager(ModelTrainerFactory())
        await manager.add_reference_images(_station_config(), "fake_model", [b"a"])

        manager.reset()

        assert manager._model_trainers == {}
