import logging

import aiohttp
import pytest

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.image import Image
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import (
    ModelForwarderConfig,
)
from edge_orchestrator.domain.models.model_forwarder.model_name import ModelName
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import (
    ModelForwarderFactory,
)
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_manager import (
    ModelForwarderManager,
)


class TestModelForwarderManager:

    @pytest.mark.integration
    async def test_model_forwarder_manager_should_return_no_prediction_with_bad_url(
        self,
        setup_test_tflite_serving: str,
        marker_image: bytes,
        caplog,
    ):
        # Given
        model_forwarder_manager = ModelForwarderManager(ModelForwarderFactory())

        item = Item(
            binaries={"camera_#1": Image(image_bytes=marker_image), "camera_#2": Image(image_bytes=marker_image)},
            cameras_metadata={
                "camera_#1": CameraConfig(
                    camera_id="camera_#1",
                    camera_type=CameraType.FAKE,
                    source_directory="fake",
                    model_forwarder_config=ModelForwarderConfig(
                        model_name=ModelName.marker_quality_control,
                        model_type=ModelType.classification,
                        model_serving_url="http://bad_url",
                        model_version="1",
                        class_names=["OK", "KO"],
                        expected_image_resolution={"width": 224, "height": 224},
                    ),
                ),
            },
        )

        # When
        with caplog.at_level(logging.ERROR):
            await model_forwarder_manager.predict_on_binaries(item)

        # Then
        records = [(record.message, record.exc_info) for record in caplog.records]
        assert len(records) == 1
        actual_record = records[0]
        assert actual_record[0] == "Error while trying to get prediction for camera camera_#1"
        assert issubclass(actual_record[1][0], aiohttp.ClientError)
        assert item.predictions == {}
