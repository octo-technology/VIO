import logging
import random
from pathlib import Path
from typing import List

from edge_orchestrator.domain.models.camera.camera_config import CameraConfig
from edge_orchestrator.domain.models.item import Image
from edge_orchestrator.domain.ports.camera.i_camera import ICamera


class FakeCamera(ICamera):
    def __init__(self, camera_config: CameraConfig):
        self._camera_config = camera_config
        self._logger = logging.getLogger(__name__)
        # TODO: use ImageExtension
        self._supported_image_extensions: List[str] = ["*.jpg", "*.png"]

    def capture(self) -> Image:
        random_image_path = self._select_random_image()
        self._logger.debug(f"Capturing image from {random_image_path}")
        return Image(image_bytes=random_image_path.open("rb").read())

    def release(self):
        pass

    def _select_random_image(self) -> Path:
        source = self._camera_config.source_directory
        selected_images = []
        for extension in self._supported_image_extensions:
            selected_images += list(source.rglob(extension))
        random_image_path = Path(random.choice(selected_images))
        return random_image_path
