from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.infrastructure.adapters.model_trainer.fake_model_trainer import (
    FakeModelTrainer,
)


class TestFakeModelTrainer:
    async def test_add_reference_images_reports_a_completed_job(self):
        # Given
        trainer = FakeModelTrainer(ModelForwarderConfig(model_name="fake_model", model_version="1"))

        # When
        job = await trainer.add_reference_images([b"a", b"b", b"c"])

        # Then
        assert job.model_name == "fake_model"
        assert job.status == "completed"
        assert job.total == 3
        assert job.processed == 3
        assert job.bank_size == 3

    async def test_get_training_job_returns_the_previously_submitted_job(self):
        # Given
        trainer = FakeModelTrainer(ModelForwarderConfig(model_name="fake_model", model_version="1"))
        submitted = await trainer.add_reference_images([b"a"])

        # When
        fetched = await trainer.get_training_job(submitted.job_id)

        # Then
        assert fetched == submitted

    async def test_get_training_job_is_lenient_about_unknown_ids(self):
        # Given
        trainer = FakeModelTrainer(ModelForwarderConfig(model_name="fake_model", model_version="1"))

        # When
        job = await trainer.get_training_job("unknown")

        # Then
        assert job.status == "completed"
        assert job.total == 0
