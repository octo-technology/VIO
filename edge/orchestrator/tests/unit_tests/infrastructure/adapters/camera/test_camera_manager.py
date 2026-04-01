from unittest.mock import MagicMock

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.models.decision import Decision
from edge_orchestrator.domain.models.item import Image, Item
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
from edge_orchestrator.infrastructure.adapters.camera.http_camera import HttpCamera


class TestCameraManager:

    def test_should_create_expected_cameras_and_store_them(
        self,
    ):
        # Given
        camera_manager = CameraManager(CameraFactory())
        station_config = StationConfig(
            station_name="test_profile",
            camera_configs={
                "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.HTTP),
                "camera_#2": CameraConfig(camera_id="camera_#2", camera_type=CameraType.HTTP),
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
        assert len(camera_manager._cameras) == 2
        assert hasattr(camera_manager, "take_pictures")
        for camera_id in ["camera_#1", "camera_#2"]:
            assert isinstance(camera_manager._cameras[camera_id], HttpCamera)

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
        _FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        mock_camera = MagicMock(spec=HttpCamera)
        mock_camera.capture.return_value = Image(image_bytes=_FAKE_JPEG)

        mock_factory = MagicMock()
        mock_factory.create_camera.return_value = mock_camera

        camera_manager = CameraManager(mock_factory)
        station_config = StationConfig(
            station_name="test_profile",
            camera_configs={
                "camera_#1": CameraConfig(camera_id="camera_#1", camera_type=CameraType.HTTP),
                "camera_#2": CameraConfig(camera_id="camera_#2", camera_type=CameraType.HTTP),
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
