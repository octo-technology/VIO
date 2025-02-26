import random
from typing import List

import pytest

from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import (
    FakeModelForwarder,
)


class TestFakeModelForwarder:

    @pytest.mark.parametrize(
        "model_type,class_names",
        [
            (ModelType.classification, ["OK", "KO"]),
            (ModelType.object_detection, ["OK", "KO"]),
            # (ModelType.segmentation, None),
        ],
    )
    async def test_fake_model_forwarder(self, model_type: ModelType, class_names: List[str]):
        # Given
        random.seed(42)
        model_forwarder_config = ModelForwarderConfig(
            model_name=ModelName.fake_model,
            model_version="1",
            model_type=model_type,
            class_names=class_names,
            expected_image_resolution={"width": 224, "height": 224},
        )
        fake_model_forwarder = FakeModelForwarder(model_forwarder_config)
        fake_binary = b"fake_binary"

        # When
        prediction = await fake_model_forwarder.predict_on_binary(fake_binary)

        # Then
        if model_type == ModelType.classification:
            assert isinstance(prediction, ClassifPrediction)
            assert prediction.label == Decision.OK and prediction.probability == 0.02501
        elif model_type == ModelType.object_detection:
            assert isinstance(prediction, DetectionPrediction)
            assert hasattr(prediction, "detected_objects")
            assert all(
                hasattr(detected_object, "label")
                and hasattr(detected_object, "location")
                and hasattr(detected_object, "objectness")
                for _, detected_object in prediction.detected_objects.items()
            )
