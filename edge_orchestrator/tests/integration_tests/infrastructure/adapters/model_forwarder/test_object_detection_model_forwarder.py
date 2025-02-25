from typing import Dict, List

import aiohttp
import pytest

from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ImageResolution,
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.infrastructure.adapters.model_forwarder.object_detection_model_forwarder import (
    ObjectDetectionModelForwarder,
)


class TestObjectDetectionModelForwarder:

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "model_name,image_resolution,class_names,expected_number_of_objects",
        [
            (
                ModelName.mobilenet_ssd_v2_coco,
                {"width": 300, "height": 300},
                ["person", "bicycle"] * 50,
                20,
            ),
            (
                ModelName.mobilenet_ssd_v2_face,
                {"width": 320, "height": 320},
                ["person", "bicycle"] * 50,
                50,
            ),
            (
                ModelName.yolo_coco_nano,
                {"width": 320, "height": 320},
                ["person", "bicycle"] * 50,
                5,
            ),
        ],
    )
    async def test_object_detection_model_forwarder_should_return_detection_prediction(
        self,
        model_name: ModelName,
        image_resolution: Dict[str, int],
        class_names: List[str],
        expected_number_of_objects: int,
        setup_test_tflite_serving: str,
        people_image: bytes,
    ):
        # Given
        image_resolution = ImageResolution(**image_resolution)
        model_forward_config = ModelForwarderConfig(
            model_name=model_name,
            model_type=ModelType.object_detection,
            model_version="1",
            class_names=class_names,
            model_serving_url=setup_test_tflite_serving,
            expected_image_resolution=image_resolution,
        )
        model_fowarder = ObjectDetectionModelForwarder(model_forward_config)

        # When
        actual_prediction = await model_fowarder.predict_on_binary(people_image)

        # Then
        assert isinstance(actual_prediction, DetectionPrediction)
        assert len(actual_prediction.detected_objects) == expected_number_of_objects
        assert actual_prediction.label is None
        if expected_number_of_objects > 0:
            assert (
                hasattr(actual_prediction.detected_objects["object_1"], "location")
                and hasattr(actual_prediction.detected_objects["object_1"], "objectness")
                and hasattr(actual_prediction.detected_objects["object_1"], "label")
            )

    @pytest.mark.integration
    async def test_object_detection_model_forwarder_should_raise_exception_with_bad_url_provided(
        self,
        setup_test_tflite_serving: str,
        marker_image: bytes,
    ):
        # Given
        image_resolution = ImageResolution(width=224, height=224)
        model_forward_config = ModelForwarderConfig(
            model_name=ModelName.mobilenet_ssd_v2_coco,
            model_type=ModelType.object_detection,
            model_version="1",
            class_names=["person", "bicycle"],
            model_serving_url=setup_test_tflite_serving,
            expected_image_resolution=image_resolution,
        )
        model_fowarder = ObjectDetectionModelForwarder(model_forward_config)
        model_fowarder._get_model_url = lambda: "http://bad_url"

        # When
        with pytest.raises(aiohttp.ClientError) as e:
            await model_fowarder.predict_on_binary(marker_image)

        # Then
        assert "nodename nor servname provided, or not known" in str(e.value)
        assert e.type == aiohttp.ClientConnectorDNSError
