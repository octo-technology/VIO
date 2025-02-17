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

    @pytest.mark.parametrize(
        "camera_id,camera_type,camera_class",
        [
            ("camera_#1", CameraType.FAKE, FakeCamera),
            ("camera_#2", CameraType.USB, WebcamCamera),
            ("camera_#3", CameraType.RASPBERRY, RaspberryPiCamera),
        ],
    )
    def test_should_return_the_specified_camera_instance(
        self, camera_id: str, camera_type: CameraType, camera_class: ICamera
    ):
        # Given
        camera_factory = CameraFactory()
        camera_config = CameraConfig(camera_id=camera_id, camera_type=camera_type)

        # When
        camera = camera_factory.create_camera(camera_config)

        # Then
        assert isinstance(camera, camera_class)
        assert hasattr(camera, "capture")
