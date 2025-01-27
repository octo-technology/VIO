import logging
from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.model_forwarder.classification_prediction import ClassifPrediction
from edge_orchestrator.domain.models.model_forwarder.model_forwarder_config import ModelForwarderConfig
from edge_orchestrator.domain.models.model_forwarder.model_type import ModelType
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_factory import ModelForwarderFactory
from edge_orchestrator.infrastructure.adapters.model_forwarder.model_forwarder_manager import ModelForwarderManager


class TestModelForwarderManager:
    def test_predict_on_binaries(self):
        # Given
        model_forwarder_factory = ModelForwarderFactory()
        model_forwarder_manager = ModelForwarderManager(model_forwarder_factory)
        item = Item(
            binaries={"camera_#1": b"fake_binary", "camera_#2": b"fake_binary"},
            cameras_metadata={
                "camera_#1": CameraConfig(
                    camera_id="camera_#1",
                    camera_type=CameraType.FAKE,
                    model_forwarder_config=ModelForwarderConfig(model_id="fake_model_#1", model_type=ModelType.FAKE),
                ),
                "camera_#2": CameraConfig(
                    camera_id="camera_#2",
                    camera_type=CameraType.RASPBERRY,
                    model_forwarder_config=ModelForwarderConfig(model_id="fake_model_#2", model_type=ModelType.FAKE),
                ),
            },
        )

        # When
        model_forwarder_manager.predict_on_binaries(item)

        # Then
        assert len(model_forwarder_manager._model_forwarders) == 2
        assert len(item.predictions) == 2
        assert isinstance(item.predictions["camera_#1"], ClassifPrediction)
        assert isinstance(item.predictions["camera_#2"], ClassifPrediction)

    def test_predict_on_binaries_should_log_warning_and_info(self, caplog):
        # Given
        model_forwarder_factory = ModelForwarderFactory()
        model_forwarder_manager = ModelForwarderManager(model_forwarder_factory)
        item = Item(
            binaries={"camera_#1": b"fake_binary", "camera_#2": b"fake_binary"},
            cameras_metadata={
                "camera_#1": CameraConfig(
                    camera_id="camera_#1",
                    camera_type=CameraType.FAKE,
                    model_forwarder_config=ModelForwarderConfig(model_id="fake_model_#1", model_type=ModelType.FAKE),
                ),
                "camera_#2": CameraConfig(
                    camera_id="camera_#2",
                    camera_type=CameraType.RASPBERRY,
                    model_forwarder_config=ModelForwarderConfig(model_id="fake_model_#1", model_type=ModelType.FAKE),
                ),
            },
        )

        # When
        with caplog.at_level(logging.INFO):
            model_forwarder_manager.predict_on_binaries(item)

        # Then
        log_messages_and_levels = [(record.message, record.levelname) for record in caplog.records]
        assert (
            "No model forwarder available to predict on item pictures! May take some extra time to instantiate.",
            "WARNING",
        ) in log_messages_and_levels
        assert ("Creating model forwarder for model_id: fake_model_#1", "INFO") in log_messages_and_levels
