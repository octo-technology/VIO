import pytest
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import ModelForwarderConfig
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import IModelForwarder
from edge_orchestrator.infrastructure.adapters.model_forwarder.detection_model_forwarder import DetectionModelForwarder
from edge_orchestrator.infrastructure.adapters.model_forwarder.detection_with_classif_model_forwarder import (
    DetectionWithClassifModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import FakeModelForwarder
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import ModelForwarderFactory


class TestModelForwarderFactory:

    @pytest.mark.parametrize(
        "model_id,model_type,model_class",
        [
            ("fake_model_#1", ModelType.FAKE, FakeModelForwarder),
            ("fake_model_#2", ModelType.OBJECT_DETECTION, DetectionModelForwarder),
            ("fake_model_#3", ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION, DetectionWithClassifModelForwarder),
        ],
    )
    def test_create_model_forwarder(self, model_id: str, model_type: ModelType, model_class: IModelForwarder):
        # Given
        model_forwarder_factory = ModelForwarderFactory()
        model_forwarder_config = ModelForwarderConfig(model_id=model_id, model_type=model_type)

        # When
        model_forwarder = model_forwarder_factory.create_model_forwarder(model_forwarder_config)

        # Then
        assert isinstance(model_forwarder, model_class)
