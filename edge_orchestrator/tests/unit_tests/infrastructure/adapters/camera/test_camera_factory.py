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
from edge_orchestrator.infrastructure.adapters.camera.usb_camera import UsbCamera


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
            ("camera_2", CameraType.WEBCAM, UsbCamera),
            ("camera_3", CameraType.USB, UsbCamera),
        ],
    )
    @patch("edge_orchestrator.infrastructure.adapters.camera.usb_camera.list_connected_usb_device")
    def test_should_return_webcam_and_usb_camera(
        self, mock_list_connected_usb_device, camera_id: str, camera_type: CameraType, camera_class: ICamera
    ):
        # Mock the list_connected_usb_device function
        mock_list_connected_usb_device.return_value = {
            ("1bcf", "2286", "pci-0000:00:14.0-usb-0:1:1.0"): {
                "vendor_name": "Sunplus_IT_Co",
                "model_name": "FHD_Camera",
                "device_path": "/dev/video0",
            }
        }

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
