from pathlib import Path
from typing import Dict, Union
import importlib

from edge_orchestrator.domain.models.camera import Camera


class RaspberryPiCamera(Camera):

    def __init__(self, id: str, settings: Dict[str, Union[str, Dict]]):
        super().__init__(id, settings)
        self.id = id
        self.settings = settings

    def capture(self) -> bytes:
        pi_camera = getattr(importlib.import_module('picamera'), 'PiCamera')
        with pi_camera() as camera:
            camera.resolution = (640, 640)
            camera.capture("./test.jpg")
            img = Path("./test.jpg")
        return img.open('rb').read()

    def apply_settings(self, custom_settings: Dict):
        self.settings = custom_settings
