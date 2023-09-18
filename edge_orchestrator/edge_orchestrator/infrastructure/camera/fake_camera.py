import random
from pathlib import Path
from typing import Dict, List, Union

from edge_orchestrator import logger
from edge_orchestrator.domain.models.camera import Camera


class FakeCamera(Camera):
    def __init__(self, id: str, settings: Dict[str, Union[str, Dict]]):
        self.id: str = id
        self.settings: Dict = settings
        self.data_folder_path: Path = Path(__file__).parents[2] / "data"
        self.image_extensions: List = ["*.jpg", "*.png"]

    def capture(self) -> bytes:
        random_image_path = self.select_random_image()
        return random_image_path.open("rb").read()

    def select_random_image(self) -> Path:
        source = self.data_folder_path / self.settings["source"]
        selected_images = []
        for extension in self.image_extensions:
            selected_images += list(source.glob(extension))
        random_image_path = Path(random.choice(selected_images))
        logger.info(str(random_image_path))
        return random_image_path

    def apply_settings(self, custom_settings: Dict):
        self.settings = custom_settings
