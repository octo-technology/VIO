import pytest

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
    FakeModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder import (
    ModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import (
    ModelForwarderFactory,
)


class TestModelForwarderFactory:

    @pytest.mark.parametrize(
        "model_name,model_class",
        [
            ("fake_model", FakeModelForwarder),
            ("pin_detection", ModelForwarder),
            ("mobilenet_ssd_v2_coco", ModelForwarder),
        ],
    )
    def test_create_model_forwarder(
        self,
        model_name: str,
        model_class: IModelForwarder,
    ):
        # Given
        model_forwarder_factory = ModelForwarderFactory()
        model_forwarder_config = ModelForwarderConfig(
            model_name=model_name,
            model_version="1",
        )

        # When
        model_forwarder = model_forwarder_factory.create_model_forwarder(model_forwarder_config)

        # Then
        assert isinstance(model_forwarder, model_class)
