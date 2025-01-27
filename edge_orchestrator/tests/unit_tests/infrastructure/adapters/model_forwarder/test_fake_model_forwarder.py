import random

import pytest
from edge_orchestrator.domain.models.model_forwarder.decision import Decision
from edge_orchestrator.domain.models.model_forwarder.detection_prediction import DetectionPrediction
from edge_orchestrator.domain.models.model_forwarder.detection_prediction_with_classif import (
    DetectionPredictionWithClassif,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import ModelForwarderConfig
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.infrastructure.adapters.model_forwarder.fake_model_forwarder import FakeModelForwarder
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import (
    ClassifPrediction,
)


class TestFakeModelForwarder:

    @pytest.mark.parametrize(
        "model_type",
        [
            ModelType.FAKE,
            ModelType.OBJECT_DETECTION,
            ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION,
        ],
    )
    def test_fake_model_forwarder(self, model_type: ModelType):
        # Given
        random.seed(42)
        model_forwarder_config = ModelForwarderConfig(model_id="fake_model", model_type=model_type)
        fake_model_forwarder = FakeModelForwarder(model_forwarder_config)
        fake_binary = b"fake_binary"

        # When
        prediction = fake_model_forwarder.predict_on_binary(fake_binary)

        # Then
        if model_type == ModelType.FAKE:
            assert isinstance(prediction, ClassifPrediction)
            assert prediction.label == Decision.OK and prediction.probability == 0.025010755222666936
        elif model_type == ModelType.OBJECT_DETECTION:
            assert isinstance(prediction, DetectionPrediction)
            assert hasattr(prediction, "detected_objects")
            assert all(
                hasattr(detected_object, "location") and hasattr(detected_object, "objectness")
                for _, detected_object in prediction.detected_objects.items()
            )
        elif model_type == ModelType.OBJECT_DETECTION_WITH_CLASSIFICATION:
            assert isinstance(prediction, DetectionPredictionWithClassif)
            assert hasattr(prediction, "detected_objects")
            assert all(
                hasattr(detected_object, "label")
                and hasattr(detected_object, "probability")
                and hasattr(detected_object, "location")
                and hasattr(detected_object, "objectness")
                for _, detected_object in prediction.detected_objects.items()
            )
