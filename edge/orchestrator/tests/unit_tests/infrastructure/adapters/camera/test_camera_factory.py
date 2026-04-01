from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.infrastructure.adapters.camera.camera_factory import (
    CameraFactory,
)
from edge_orchestrator.infrastructure.adapters.camera.http_camera import HttpCamera


class TestCameraFactory:
    def test_should_return_http_camera_instance(self):
        # Given
        camera_factory = CameraFactory()
        camera_config = CameraConfig(camera_id="camera_#1", camera_type=CameraType.HTTP)

        # When
        camera = camera_factory.create_camera(camera_config)

        # Then
        assert isinstance(camera, HttpCamera)
        assert isinstance(camera, ICamera)
        assert hasattr(camera, "capture")
