import logging

from edge_orchestrator.domain.models.binary import Image
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.item import Item
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
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_manager import (
    ModelForwarderManager,
)


class TestModelForwarderManager:
    async def test_predict_on_binaries_should_get_predictions_and_log_warning_and_info(
        self, mocked_model_forwarder_factory, caplog
    ):
        # Given

        model_forwarder_manager = ModelForwarderManager(mocked_model_forwarder_factory)
        item = Item(
            binaries={"camera_#1": Image(image_bytes=b"fake_binary"), "camera_#2": Image(image_bytes=b"fake_binary")},
            cameras_metadata={
                "camera_#1": CameraConfig(
                    camera_id="camera_#1",
                    camera_type=CameraType.FAKE,
                    source_directory="fake",
                    model_forwarder_config=ModelForwarderConfig(
                        model_name=ModelName.fake_model,
                        model_type=ModelType.classification,
                        model_version="1",
                        class_names=["OK", "KO"],
                        expected_image_resolution={"width": 224, "height": 224},
                    ),
                ),
                "camera_#2": CameraConfig(
                    camera_id="camera_#2",
                    camera_type=CameraType.RASPBERRY,
                    source_directory="fake",
                    model_forwarder_config=ModelForwarderConfig(
                        model_name=ModelName.fake_model,
                        model_type=ModelType.object_detection,
                        model_version="1",
                        class_names=["OK", "KO"],
                        expected_image_resolution={"width": 224, "height": 224},
                    ),
                ),
            },
        )

        # When
        with caplog.at_level(logging.INFO):
            await model_forwarder_manager.predict_on_binaries(item)

        # Then
        log_messages_and_levels = [(record.message, record.levelname) for record in caplog.records]
        assert len(model_forwarder_manager._model_forwarders) == 2
        assert len(item.predictions) == 2
        assert isinstance(item.predictions["camera_#1"], ClassifPrediction)
        assert isinstance(item.predictions["camera_#2"], DetectionPrediction)
        assert (
            "No model forwarder available to predict on item pictures! May take some extra time to instantiate.",
            "WARNING",
        ) in log_messages_and_levels
        assert ("Creating model forwarder for model_id: fake_model_classification_1", "INFO") in log_messages_and_levels
        assert (
            "Creating model forwarder for model_id: fake_model_object_detection_1",
            "INFO",
        ) in log_messages_and_levels
