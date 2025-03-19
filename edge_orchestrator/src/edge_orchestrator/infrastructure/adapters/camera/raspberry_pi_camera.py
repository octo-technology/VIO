import logging
from io import BytesIO

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Image
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class RaspberryPiCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        self._picam2 = None
        try:
            from picamera2 import Picamera2

            self._picam2 = Picamera2()
            self.capture_config = self._picam2.create_still_configuration(buffer_count=1)
            self._picam2.start()
        except ModuleNotFoundError:
            self._logger.error(
                "PiCamera module not found, please make sure it is installed. Capture method will not work."
            )

    def capture(self) -> Image:
        stream = BytesIO()
        self._picam2.capture_file(stream, format="jpeg")
        stream.seek(0)
        return Image(image_bytes=stream.read())

    def release(self):
        try:
            if self._picam2:
                self._picam2.close()
        except RuntimeError:
            self._logger.exception("Camera closing failed")
