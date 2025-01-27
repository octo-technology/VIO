import logging
from io import BytesIO

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class RaspberryPiCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        from picamera import PiCamera

        self.pi_camera = PiCamera()
        self.pi_camera.start_preview()

    def capture(self) -> bytes:
        stream = BytesIO()
        self.pi_camera.capture(stream, "jpeg")
        stream.seek(0)
        return stream.read()

    def get_camera_config(self) -> CameraConfig:
        return self._camera_config
