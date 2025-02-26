import pytest

from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.domain.ports.model_forwarder.i_model_forwarder import (
    IModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.classif_model_forwarder import (
    ClassifModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
    FakeModelForwarder,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import (
    ModelForwarderFactory,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.object_detection_model_forwarder import (
    ObjectDetectionModelForwarder,
)


class TestModelForwarderFactory:

    @pytest.mark.parametrize(
        "model_name,model_type,model_class",
        [
            (ModelName.fake_model, ModelType.classification, FakeModelForwarder),
            (ModelName.pin_detection, ModelType.classification, ClassifModelForwarder),
            (
                ModelName.mobilenet_ssd_v2_coco,
                ModelType.object_detection,
                ObjectDetectionModelForwarder,
            ),
        ],
    )
    def test_create_model_forwarder(
        self,
        model_name: ModelName,
        model_type: ModelType,
        model_class: IModelForwarder,
    ):
        # Given
        model_forwarder_factory = ModelForwarderFactory()
        model_forwarder_config = ModelForwarderConfig(
            model_name=model_name,
            model_version="1",
            model_type=model_type,
            class_names=["OK", "KO"],
            expected_image_resolution={"width": 224, "height": 224},
        )

        # When
        model_forwarder = model_forwarder_factory.create_model_forwarder(model_forwarder_config)

        # Then
        assert isinstance(model_forwarder, model_class)
