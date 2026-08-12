from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.infrastructure.adapters.model_trainer.fake_model_trainer import (
    FakeModelTrainer,
)
from edge_orchestrator.infrastructure.adapters.model_trainer.model_trainer import (
    ModelTrainer,
)
from edge_orchestrator.infrastructure.adapters.model_trainer.model_trainer_factory import (
    ModelTrainerFactory,
)


class TestModelTrainerFactory:
    def test_creates_a_fake_trainer_for_the_fake_model(self):
        factory = ModelTrainerFactory()

        trainer = factory.create_model_trainer(ModelForwarderConfig(model_name="fake_model"))

        assert isinstance(trainer, FakeModelTrainer)

    def test_creates_an_http_trainer_for_a_real_model(self):
        factory = ModelTrainerFactory()

        trainer = factory.create_model_trainer(
            ModelForwarderConfig(model_name="my_part", model_serving_url="http://edge_anomaly_serving:8502")
        )

        assert isinstance(trainer, ModelTrainer)
