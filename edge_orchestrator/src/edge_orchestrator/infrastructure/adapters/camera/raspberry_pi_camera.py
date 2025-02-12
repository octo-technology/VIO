import importlib
import logging
from io import BytesIO

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Image
from edge_orchestrator.domain.ports.camera.i_camera import ICamera
from edge_orchestrator.infrastructure.adapters.camera.fake_camera import FakeCamera


class RaspberryPiCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        try:
            PiCamera = getattr(importlib.import_module("picamera"), "PiCamera")

            self.pi_camera = PiCamera()
            self.pi_camera.start_preview()
        except ModuleNotFoundError:
            self._logger.error("PiCamera module not found. Please make sure it is installed. Defaulting to FakeCamera.")
            self.capture = FakeCamera(camera_config).capture

    def capture(self) -> Image:
        stream = BytesIO()
        self.pi_camera.capture(stream, "jpeg")
        stream.seek(0)
        return Image(image_bytes=stream.read())
