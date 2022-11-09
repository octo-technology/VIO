import random
from pathlib import Path
from typing import Dict, Union

from supervisor import logger
from supervisor.domain.models.camera import Camera
from supervisor.environment.config import Config


class FakeCamera(Camera):

    def __init__(self, id: str, settings: Dict[str, Union[str, Dict]]):
        super().__init__(id, settings)
        self.id = id
        self.settings = settings
        self.data_folder_path = Config.ROOT_PATH / 'data'

    def capture(self) -> bytes:
        random_image_path = self.select_random_image()
        return random_image_path.open('rb').read()

    def select_random_image(self) -> Path:
        input_images_folder = self.data_folder_path / self.settings['input_images_folder']
        random_image_path = Path(random.choice(list(input_images_folder.glob('*.jpg'))))
        logger.info(str(random_image_path))
        return random_image_path

    def apply_settings(self, custom_settings: Dict):
        self.settings = custom_settings
