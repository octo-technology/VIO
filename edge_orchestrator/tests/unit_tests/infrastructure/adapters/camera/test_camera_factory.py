from unittest.mock import patch

import pytest

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.infrastructure.adapters.camera.camera_factory import (
    CameraFactory,
)
from edge_orchestrator.infrastructure.adapters.camera.fake_camera import FakeCamera
from edge_orchestrator.infrastructure.adapters.camera.raspberry_pi_camera import (
    RaspberryPiCamera,
)
from edge_orchestrator.infrastructure.adapters.camera.webcam_camera import WebcamCamera


class TestCameraFactory:

    def test_should_create_a_fake_camera(
        self,
    ):
        # Given
        camera_factory = CameraFactory()
        camera_config = CameraConfig(camera_id="camera_1", camera_type=CameraType.FAKE, source_directory="fake")

        # When
        camera = camera_factory.create_camera(camera_config)

        # Then
        assert isinstance(camera, FakeCamera)
        assert hasattr(camera, "capture")

    @pytest.mark.parametrize(
        "camera_id,camera_type,camera_class",
        [
            ("camera_2", CameraType.WEBCAM, WebcamCamera),
            ("camera_3", CameraType.USB, WebcamCamera),
        ],
    )
    @patch("edge_orchestrator.domain.models.camera.camera_config.get_camera_device_node")
    def test_should_return_webcam_and_usb_camera(
        self, mock_get_camera_device_node, camera_id: str, camera_type: CameraType, camera_class: ICamera
    ):
        # Mock the get_camera_device_node function
        mock_get_camera_device_node.return_value = "/dev/video0"

        # Given
        camera_factory = CameraFactory()
        camera_config = CameraConfig(
            camera_id=camera_id, camera_type=camera_type, camera_vendor="test", camera_serial_number="test"
        )

        # When
        camera = camera_factory.create_camera(camera_config)

        # Then
        assert isinstance(camera, camera_class)
        assert hasattr(camera, "capture")
        camera.release()

    def test_should_create_a_raspberry_camera(
        self,
    ):
        # Given
        camera_factory = CameraFactory()
        camera_config = CameraConfig(camera_id="camera_1", camera_type=CameraType.RASPBERRY)

        # When
        camera = camera_factory.create_camera(camera_config)

        # Then
        assert isinstance(camera, RaspberryPiCamera)
        assert hasattr(camera, "capture")
        camera.release()
