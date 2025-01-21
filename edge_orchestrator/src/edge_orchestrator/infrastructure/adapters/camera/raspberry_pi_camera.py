import importlib
import logging
from pathlib import Path

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class RaspberryPiCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)

    def capture(self) -> bytes:
        pi_camera = getattr(importlib.import_module("picamera"), "PiCamera")
        with pi_camera() as camera:
            camera.resolution = (640, 640)
            camera.capture("./test.jpg")
            img = Path("./test.jpg")
        return img.open("rb").read()

    def get_camera_config(self) -> CameraConfig:
        return self._camera_config
