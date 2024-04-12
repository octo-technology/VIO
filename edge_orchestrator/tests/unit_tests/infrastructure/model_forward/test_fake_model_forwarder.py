import random

import numpy as np
import pytest

from edge_orchestrator.domain.models.model_infos import ModelInfos
from edge_orchestrator.domain.ports.model_forward import Labels
from edge_orchestrator.infrastructure.model_forward.fake_model_forward import (
    FakeModelForward,
)


@pytest.mark.asyncio
class TestFakeModelForwarder:
    async def test_perform_inference_should_return_classification_results(self):
        # Given
        np.random.seed(42)
        random.seed(42)
        fake_model_forwarder = FakeModelForward()
        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="inception",
            category="classification",
            version="1.2",
            camera_id="camera_id1",
            image_resolution=[640, 640],
        )
        binary_data = bytes([])

        expected = {"full_image": {"label": Labels.OK.value, "probability": 0.3745401188473625}}

        # When
        actual = await fake_model_forwarder.perform_inference(model_inference_version, binary_data, "full_image")

        # Then
        assert actual == expected

    async def test_perform_inference_should_return_object_detection_results(self):
        # Given
        np.random.seed(42)
        random.seed(42)
        fake_model_forwarder = FakeModelForward()
        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_v1_640x640",
            category="object_detection",
            version="1",
            camera_id="camera_id1",
            image_resolution=[640, 640],
        )
        binary_data = bytes([])

        expected = {
            "full_image_object_1": {
                "location": [4, 112, 244, 156],
                "objectness": 0.3745401188473625,
            },
            "full_image_object_2": {
                "location": [4, 112, 244, 156],
                "objectness": 0.9507143064099162,
            },
        }

        # When
        actual = await fake_model_forwarder.perform_inference(model_inference_version, binary_data, "full_image")

        # Then
        assert actual == expected

    async def test_perform_inference_should_return_object_detection_with_classification_results(
        self,
    ):
        # Given
        np.random.seed(42)
        random.seed(42)
        fake_model_forwarder = FakeModelForward()
        model_inference_version = ModelInfos(
            id="model1",
            depends_on=[],
            name="mobilenet_v1_640x640_detect_classif",
            category="object_detection_with_classification",
            version="1.3",
            camera_id="camera_id1",
        )
        binary_data = bytes([])

        expected = {
            "full_image_object_1": {
                "label": "OK",
                "objectness": 0.3745401188473625,
                "location": [4, 112, 244, 156],
                "probability": 0.9507143064099162,
            },
            "full_image_object_2": {
                "label": "OK",
                "objectness": 0.7319939418114051,
                "location": [4, 112, 244, 156],
                "probability": 0.5986584841970366,
            },
        }

        # When
        actual = await fake_model_forwarder.perform_inference(model_inference_version, binary_data, "full_image")

        # Then
        assert actual == expected
