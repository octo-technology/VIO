import subprocess
from pathlib import Path
from typing import Dict, Union

from edge_orchestrator import logger
from edge_orchestrator.domain.models.camera import Camera


class UsbCamera(Camera):
    def __init__(self, id: str, settings: Dict[str, Union[str, Dict]]):
        self.id = id
        self.settings = settings

    def capture(self) -> bytes:
        resolution = "640x640"
        source = self.settings["source"]
        img_save_path = f"{source}.jpg".replace("/", "")
        cmd = f"fswebcam -r {resolution} -S 3 --jpeg 50 --save {img_save_path} -d {source}"
        cmd_feedback = subprocess.run([cmd], shell=True)
        logger.info(f"Camera exit code: {cmd_feedback.returncode}")
        return Path(img_save_path).open("rb").read()

    def apply_settings(self, custom_settings: Dict):
        self.settings = custom_settings
