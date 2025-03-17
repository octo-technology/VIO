import logging

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.camera.camera_type import CameraType
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.domain.ports.camera.i_camera_factory import ICameraFactory


class CameraFactory(ICameraFactory):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def create_camera(self, camera_config: CameraConfig) -> ICamera:
        if camera_config.camera_type == CameraType.FAKE:
            from edge_orchestrator.infrastructure.adapters.camera.fake_camera import (
                FakeCamera,
            )

            return FakeCamera(camera_config)
        elif camera_config.camera_type == CameraType.RASPBERRY:
            from edge_orchestrator.infrastructure.adapters.camera.raspberry_pi_camera import (
                RaspberryPiCamera,
            )

            return RaspberryPiCamera(camera_config)
        elif camera_config.camera_type == CameraType.WEBCAM:
            from edge_orchestrator.infrastructure.adapters.camera.webcam_camera import (
                WebcamCamera,
            )

            return WebcamCamera(camera_config)
        
        elif camera_config.camera_type == CameraType.USB:
            from edge_orchestrator.infrastructure.adapters.camera.usb_camera import (
                UsbCamera,
            )

            return UsbCamera(camera_config)
        else:
            raise ValueError(f"Camera type ({camera_config.camera_type}) is not supported.")
