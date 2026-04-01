import aiohttp
import pytest

from edge_orchestrator.domain.models.model_forwarder.detection_prediction import (
    DetectionPrediction,
)
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder import (
    ModelForwarder,
)


class TestModelForwarderObjectDetection:
    @pytest.mark.integration
    @pytest.mark.parametrize(
        "model_name,min_objects,max_objects",
        [
            ("mobilenet_ssd_v2_coco", 20, 20),
            ("mobilenet_ssd_v2_face", 50, 50),
            ("yolo_coco_nano", 1, 10),
        ],
    )
    async def test_model_forwarder_should_return_detection_prediction(
        self,
        model_name: str,
        min_objects: int,
        max_objects: int,
        setup_test_tflite_serving: str,
        people_image: bytes,
    ):
        # Given
        model_forward_config = ModelForwarderConfig(
            model_name=model_name,
            model_version="1",
            model_serving_url=setup_test_tflite_serving,
        )
        model_forwarder = ModelForwarder(model_forward_config)

        # When
        actual_prediction = await model_forwarder.predict_on_binary(people_image)

        # Then
        assert isinstance(actual_prediction, DetectionPrediction)
        assert min_objects <= len(actual_prediction.detected_objects) <= max_objects
        assert actual_prediction.label is None
        if len(actual_prediction.detected_objects) > 0:
            assert (
                hasattr(actual_prediction.detected_objects["object_1"], "location")
                and hasattr(actual_prediction.detected_objects["object_1"], "objectness")
                and hasattr(actual_prediction.detected_objects["object_1"], "label")
            )

    @pytest.mark.integration
    async def test_model_forwarder_should_raise_exception_with_bad_url_provided(
        self,
        setup_test_tflite_serving: str,
        marker_image: bytes,
    ):
        # Given
        model_forward_config = ModelForwarderConfig(
            model_name="mobilenet_ssd_v2_coco",
            model_version="1",
            model_serving_url=setup_test_tflite_serving,
        )
        model_forwarder = ModelForwarder(model_forward_config)
        model_forwarder._get_model_url = lambda: "http://bad_url"

        # When
        with pytest.raises(aiohttp.ClientError) as e:
            await model_forwarder.predict_on_binary(marker_image)

        # Then
        assert "Cannot connect to host" in str(e.value)
        assert e.type == aiohttp.ClientConnectorDNSError
