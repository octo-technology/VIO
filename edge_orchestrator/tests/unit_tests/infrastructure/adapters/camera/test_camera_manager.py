from pathlib import Path

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Item
from edge_orchestrator.domain.models.item_rule.item_rule_config import ItemRuleConfig
from edge_orchestrator.domain.models.item_rule.item_rule_type import ItemRuleType
from edge_orchestrator.domain.models.station_config import StationConfig
from edge_orchestrator.domain.models.storage.storage_config import StorageConfig
from edge_orchestrator.infrastructure.adapters.camera.camera_factory import (
    CameraFactory,
)
from edge_orchestrator.infrastructure.adapters.camera.camera_manager import (
    CameraManager,
)
from edge_orchestrator.infrastructure.adapters.camera.fake_camera import FakeCamera
from edge_orchestrator.infrastructure.adapters.camera.raspberry_pi_camera import (
    RaspberryPiCamera,
)
from edge_orchestrator.infrastructure.adapters.camera.webcam_camera import WebcamCamera


class TestCameraManager:

    def test_should_create_expected_cameras_and_store_them(
        self,
    ):
        # Given
        camera_id_camera_classes = [
            ("camera_#1", FakeCamera),
            ("camera_#2", WebcamCamera),
            ("camera_#3", RaspberryPiCamera),
        ]

        camera_manager = CameraManager(CameraFactory())
        station_config = StationConfig(
            station_name="test_profile",
            camera_configs={
                "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.FAKE, source_directory="fake"),
                "camera_#2": CameraConfig(
                    camera_id="camera_#2",
                    camera_type=CameraType.WEBCAM,
                    camera_vendor="test",
                    camera_serial_number="test",
                ),
                "camera_#3": CameraConfig(camera_id="camera_#3", camera_type=CameraType.RASPBERRY),
            },
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.OK, threshold=1
            ),
        )

        # When
        camera_manager.create_cameras(station_config)

        # Then
        assert hasattr(camera_manager, "_cameras")
        assert len(camera_manager._cameras) == 3
        assert hasattr(camera_manager, "take_pictures")
        for camera_id, camera_class in camera_id_camera_classes:
            assert isinstance(camera_manager._cameras[camera_id], camera_class)
            if not isinstance(camera_manager._cameras[camera_id], FakeCamera):
                camera_manager._cameras[camera_id].release()

    def test_should_raise_exception_without_creating_cameras_first(
        self,
        caplog,
    ):
        # Given
        camera_manager = CameraManager(CameraFactory())

        # When
        assert len(camera_manager._cameras) == 0
        with caplog.at_level("WARNING"):
            camera_manager.take_pictures(Item())

        # Then
        log_messages = [(record.msg, record.levelname) for record in caplog.records]
        assert ("No camera available to take picture!", "ERROR") in log_messages

    def test_should_take_pictures_after_creating_cameras(
        self,
    ):
        # Given
        camera_ids = ["camera_#1", "camera_#2"]
        source_directory = Path(__file__).resolve().parents[5] / "fake_images"
        CameraFactory.create_camera = lambda s, c: FakeCamera(
            CameraConfig(camera_id="camera_#1", camera_type=CameraType.FAKE, source_directory=source_directory)
        )
        mock_camera_factory = CameraFactory()
        camera_manager = CameraManager(mock_camera_factory)
        station_config = StationConfig(
            station_name="test_profile",
            camera_configs={
                "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.USB, source_directory="fake"),
                "camera_#2": CameraConfig(
                    camera_id="camera_#2", camera_type=CameraType.RASPBERRY, source_directory="fake"
                ),
            },
            binary_storage_config=StorageConfig(),
            metadata_storage_config=StorageConfig(),
            item_rule_config=ItemRuleConfig(
                item_rule_type=ItemRuleType.MIN_THRESHOLD_RULE, expected_decision=Decision.KO, threshold=1
            ),
        )
        item = Item()

        # When
        camera_manager.create_cameras(station_config)
        camera_manager.take_pictures(item)

        # Then
        assert len(item.binaries) == 2
        for camera_id in camera_ids:
            assert (
                isinstance(item.binaries[camera_id].image_bytes, bytes)
                and len(item.binaries[camera_id].image_bytes) > 0
            )
